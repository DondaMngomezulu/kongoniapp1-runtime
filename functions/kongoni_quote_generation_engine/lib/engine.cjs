'use strict';
// ENG-S01-QUOTATION v0.1.0 -- controlled quotation composition; never an approval engine.
const { createHash } = require('node:crypto');
const { assessAIProposal } = require('./intent.cjs');
const { crmDraftCandidate } = require('./crm.cjs');

const ENGINE_ID = 'ENG-S01-QUOTATION';
const VERSION = '0.1.0';
const TYPES = new Set(['CASH_SALE', 'OPERATING_LEASE', 'DRY_RENTAL']);
const BASES = new Set(['ONE_TIME', 'FIXED_MONTHLY', 'HOURLY_VARIABLE']);
const GATES = ['catalogue', 'pricing', 'tax', 'commercial_terms', 'counterparty',
  'stock', 'issuer', 'document_template'];
const LEASE_GATES = ['credit', 'legal', 'lifecycle_cost', 'finance'];

class ContractError extends Error {
  constructor(code, detail) { super(detail || code); this.name = 'ContractError'; this.code = code; }
}
function must(value, code) { if (!value) throw new ContractError(code); }
function id(value, code) {
  must(typeof value === 'string' && /^[A-Za-z0-9_.:\/-]{1,120}$/.test(value), code);
  return value;
}
function minor(value, code) {
  must(Number.isSafeInteger(value) && value >= 0, code);
  return BigInt(value);
}
function quantity(value, code) {
  must(Number.isSafeInteger(value) && value > 0 && value <= 100000, code);
  return BigInt(value);
}
function date(value, code) {
  must(typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value), code);
  const parsed = new Date(value + 'T00:00:00.000Z');
  must(!Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value, code);
  return value;
}
function number(n, code) {
  must(n >= 0n && n <= BigInt(Number.MAX_SAFE_INTEGER), code);
  return Number(n);
}
function roundTax(amountMinor, rateBps) {
  return (amountMinor * BigInt(rateBps) + 5000n) / 10000n;
}
function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.keys(value).sort().map(k => [k, canonical(value[k])]));
  }
  return value;
}
function validateRequest(req) {
  must(req && typeof req === 'object' && !Array.isArray(req), 'REQUEST_REQUIRED');
  must(req.schema_version === '1.0', 'SCHEMA_VERSION_UNSUPPORTED');
  id(req.request_id, 'REQUEST_ID_INVALID');
  id(req.tenant_id, 'TENANT_ID_INVALID');
  id(req.deal_id, 'DEAL_ID_INVALID');
  id(req.account_id, 'ACCOUNT_ID_INVALID');
  must(TYPES.has(req.quote_type), 'QUOTE_TYPE_INVALID');
  must(req.currency === 'ZAR', 'CURRENCY_PROFILE_UNSUPPORTED');
  must(typeof req.subject === 'string' && req.subject.trim().length > 0 && req.subject.length <= 240, 'SUBJECT_INVALID');
  date(req.quote_date, 'QUOTE_DATE_INVALID');
  date(req.valid_until, 'VALID_UNTIL_INVALID');
  must(req.valid_until >= req.quote_date, 'VALIDITY_ORDER_INVALID');
  const p = req.provenance;
  must(p && p.source_system === 'Zoho CRM', 'CRM_SOURCE_REQUIRED');
  for (const key of ['snapshot_id', 'catalogue_version', 'policy_version', 'document_template_id']) {
    id(p[key], 'SOURCE_REF_INVALID:' + key);
  }
  must(Array.isArray(req.lines) && req.lines.length > 0 && req.lines.length <= 100, 'LINES_INVALID');
  must(req.gates && typeof req.gates === 'object' && !Array.isArray(req.gates), 'GATES_REQUIRED');
  must(req.gate_evidence && typeof req.gate_evidence === 'object' && !Array.isArray(req.gate_evidence), 'GATE_EVIDENCE_REQUIRED');
  const seen = new Set();
  for (const line of req.lines) {
    must(line && typeof line === 'object', 'LINE_INVALID');
    id(line.line_id, 'LINE_ID_INVALID');
    id(line.product_id, 'PRODUCT_ID_INVALID');
    id(line.price_source_ref, 'PRICE_SOURCE_REF_REQUIRED');
    id(line.tax_source_ref, 'TAX_SOURCE_REF_REQUIRED');
    id(line.price_rule_version, 'PRICE_RULE_VERSION_REQUIRED');
    must(line.price_status === 'APPROVED', 'PRICE_NOT_APPROVED:' + line.line_id);
    must(BASES.has(line.basis), 'BASIS_INVALID:' + line.line_id);
    must(!seen.has(line.line_id), 'DUPLICATE_LINE_ID');
    seen.add(line.line_id);
    quantity(line.quantity, 'QUANTITY_INVALID:' + line.line_id);
    minor(line.unit_price_minor, 'PRICE_MINOR_INVALID:' + line.line_id);
    must(Number.isInteger(line.tax_rate_bps) && line.tax_rate_bps >= 0 && line.tax_rate_bps <= 10000,
      'TAX_BPS_INVALID:' + line.line_id);
    if (line.basis === 'HOURLY_VARIABLE') {
      must(Number.isSafeInteger(line.planned_hours_per_unit) && line.planned_hours_per_unit >= 0,
        'PLANNED_HOURS_REQUIRED:' + line.line_id);
    } else {
      must(line.planned_hours_per_unit == null, 'UNEXPECTED_PLANNED_HOURS:' + line.line_id);
    }
    if (req.quote_type === 'CASH_SALE') must(line.basis === 'ONE_TIME', 'CASH_BASIS_INVALID');
  }
}
function composeDraft(request, { sourceVerified = false, aiProposal = null } = {}) {
  validateRequest(request);
  const sums = { ONE_TIME: { sub: 0n, tax: 0n }, FIXED_MONTHLY: { sub: 0n, tax: 0n },
    HOURLY_VARIABLE: { sub: 0n, tax: 0n } };
  const detail = [];
  for (const l of request.lines) {
    const usage = l.basis === 'HOURLY_VARIABLE' ? BigInt(l.planned_hours_per_unit) : 1n;
    const extended = minor(l.unit_price_minor, 'PRICE_INVALID') * quantity(l.quantity, 'QUANTITY_INVALID') * usage;
    const tax = roundTax(extended, l.tax_rate_bps);
    sums[l.basis].sub += extended;
    sums[l.basis].tax += tax;
    detail.push({ line_id: l.line_id, product_id: l.product_id, quantity: l.quantity, basis: l.basis,
      unit_price_minor: l.unit_price_minor, planned_hours_per_unit: l.planned_hours_per_unit ?? null,
      amount_ex_tax_minor: number(extended, 'LINE_OVERFLOW'), tax_minor: number(tax, 'TAX_OVERFLOW'),
      amount_inc_tax_minor: number(extended + tax, 'LINE_OVERFLOW'),
      price_source_ref: l.price_source_ref, price_rule_version: l.price_rule_version,
      tax_source_ref: l.tax_source_ref });
  }
  const totals = {};
  for (const [basis, x] of Object.entries(sums)) {
    totals[basis] = { ex_tax_minor: number(x.sub, 'TOTAL_OVERFLOW'),
      tax_minor: number(x.tax, 'TOTAL_OVERFLOW'), inc_tax_minor: number(x.sub + x.tax, 'TOTAL_OVERFLOW') };
  }
  // Monthly amounts are *illustrations*, NOT total contractual lease obligations or future invoices.
  const monthly = sums.FIXED_MONTHLY.sub + sums.HOURLY_VARIABLE.sub;
  const monthlyTax = sums.FIXED_MONTHLY.tax + sums.HOURLY_VARIABLE.tax;
  totals.ESTIMATED_MONTHLY = { ex_tax_minor: number(monthly, 'TOTAL_OVERFLOW'),
    tax_minor: number(monthlyTax, 'TOTAL_OVERFLOW'),
    inc_tax_minor: number(monthly + monthlyTax, 'TOTAL_OVERFLOW') };
  const required = GATES.concat(request.quote_type === 'CASH_SALE' ? [] : LEASE_GATES);
  const checks = required.map(gate => ({ gate, passed: request.gates[gate] === true,
    evidence_ref: request.gate_evidence?.[gate] || null }));
  const blocks = checks.filter(c => !c.passed || !c.evidence_ref).map(c => 'GATE_NOT_EVIDENCED:' + c.gate);
  if (!sourceVerified) blocks.push('SOURCE_ADAPTER_NOT_VERIFIED');
  const ai = assessAIProposal(aiProposal, request);
  blocks.push(...ai.blocks);
  const digest = createHash('sha256').update(JSON.stringify(canonical({ request, ai_proposal: aiProposal }))).digest('hex');
  const draftId = 'QPREVIEW-' + digest.slice(0, 20);
  const result = { engine_id: ENGINE_ID, engine_version: VERSION, schema_version: '1.0',
    draft_id: draftId, correlation_id: request.request_id, tenant_id: request.tenant_id,
    quote_type: request.quote_type, quote_date: request.quote_date, valid_until: request.valid_until,
    currency: request.currency, totals, lines: detail, gate_checks: checks,
    ai_review: ai, release_blockers: Array.from(new Set(blocks)),
    review_status: blocks.length ? 'HOLD' : 'READY_FOR_INTERNAL_REVIEW',
    customer_issue_authorised: false, crm_write_authorised: false,
    provenance: { source_system: request.provenance.source_system, snapshot_id: request.provenance.snapshot_id,
      catalogue_version: request.provenance.catalogue_version,
      policy_version: request.provenance.policy_version,
      document_template_id: request.provenance.document_template_id,
      source_verified: sourceVerified, result_hash: digest } };
  result.crm_draft_candidate = crmDraftCandidate(request, result);
  return result;
}
module.exports = { composeDraft, validateRequest, ContractError, ENGINE_ID, VERSION };
