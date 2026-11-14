'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { composeDraft, ContractError } = require('../lib/engine.cjs');
const { interpretRequirements } = require('../lib/intent.cjs');

function request(type = 'CASH_SALE') {
  const req = { schema_version: '1.0', request_id: 'REQ-001', tenant_id: 'SYNTHETIC-TENANT',
    deal_id: 'SYNTHETIC-DEAL', account_id: 'SYNTHETIC-ACCOUNT', quote_type: type,
    currency: 'ZAR', subject: 'Synthetic equipment quotation', quote_date: '2026-10-09',
    valid_until: '2026-10-23',
    provenance: { source_system: 'Zoho CRM', snapshot_id: 'SYNTHETIC-001',
      catalogue_version: 'SYN-1', policy_version: 'SYN-1', document_template_id: 'SYN-TEMPLATE-001' },
    lines: [{ line_id: 'L01', product_id: 'TEST-MACHINE', quantity: 2,
      basis: 'ONE_TIME', unit_price_minor: 123450, price_status: 'APPROVED',
      price_source_ref: 'SYN-PRC-001', price_rule_version: 'SYN-1',
      tax_rate_bps: 1500, tax_source_ref: 'SYN-TAX-001' }],
    gates: { catalogue: true, pricing: true, tax: true, commercial_terms: true,
      counterparty: true, stock: true, issuer: true, document_template: true,
      credit: true, legal: true, lifecycle_cost: true, finance: true },
    gate_evidence: { catalogue: 'E-CATALOGUE', pricing: 'E-PRICING', tax: 'E-TAX',
      commercial_terms: 'E-TERMS', counterparty: 'E-PARTY', stock: 'E-STOCK',
      issuer: 'E-ISSUER', document_template: 'E-TEMPLATE', credit: 'E-CREDIT',
      legal: 'E-LEGAL', lifecycle_cost: 'E-LCC', finance: 'E-FINANCE' } };
  if (type !== 'CASH_SALE') {
    req.lines = [
      { ...req.lines[0], line_id: 'L-FIXED', quantity: 1, basis: 'FIXED_MONTHLY',
        unit_price_minor: 250000 },
      { ...req.lines[0], line_id: 'L-USAGE', quantity: 1, basis: 'HOURLY_VARIABLE',
        planned_hours_per_unit: 100, unit_price_minor: 12345 }
    ];
  }
  return req;
}

test('cash: rounded ZAR minor units and VAT from governed input', () => {
  const res = composeDraft(request());
  assert.equal(res.totals.ONE_TIME.ex_tax_minor, 246900);
  assert.equal(res.totals.ONE_TIME.tax_minor, 37035);
  assert.equal(res.totals.ONE_TIME.inc_tax_minor, 283935);
  assert.equal(res.review_status, 'HOLD');
  assert.equal(res.customer_issue_authorised, false);
  assert.equal(res.crm_draft_candidate.integration_state, 'NOT_WRITE_READY');
});

test('cash: trusted-adapter can clear source hold but never issue customer quote', () => {
  const res = composeDraft(request(), { sourceVerified: true });
  assert.equal(res.review_status, 'READY_FOR_INTERNAL_REVIEW');
  assert.equal(res.customer_issue_authorised, false);
  assert.equal(res.crm_write_authorised, false);
});

test('operating lease: fixed and planned hourly streams remain distinguishable', () => {
  const res = composeDraft(request('OPERATING_LEASE'));
  assert.equal(res.totals.FIXED_MONTHLY.ex_tax_minor, 250000);
  assert.equal(res.totals.HOURLY_VARIABLE.ex_tax_minor, 1234500);
  assert.equal(res.totals.ESTIMATED_MONTHLY.ex_tax_minor, 1484500);
  assert.equal(res.totals.ONE_TIME.ex_tax_minor, 0);
  assert.equal(res.lines[1].planned_hours_per_unit, 100);
});

test('dry rental: same time-unit separation as operating lease', () => {
  const res = composeDraft(request('DRY_RENTAL'));
  assert.equal(res.totals.ESTIMATED_MONTHLY.ex_tax_minor, 1484500);
});

test('missing approval or evidence creates review hold', () => {
  const req = request();
  req.gates.tax = false;
  delete req.gate_evidence.pricing;
  const r = composeDraft(req, { sourceVerified: true });
  assert.ok(r.release_blockers.includes('GATE_NOT_EVIDENCED:tax'));
  assert.ok(r.release_blockers.includes('GATE_NOT_EVIDENCED:pricing'));
});

test('AI cannot override price, tax or product identity', () => {
  const p = { tenant_id: 'SYNTHETIC-TENANT', model_id: 'MOCK-MODEL', prompt_version: '1',
    reviewed_evidence_ref: 'EXAMPLE', price: 1,
    product_intents: [{ product_id: 'NONEXISTENT', quantity: 2, evidence_ref: 'SYN' }] };
  const res = composeDraft(request(), { aiProposal: p, sourceVerified: true });
  assert.ok(res.release_blockers.includes('AI_AUTHORITY_OVERRIDE_REJECTED'));
  assert.ok(res.release_blockers.includes('AI_PRODUCT_OR_QUANTITY_UNVERIFIED'));
  assert.equal(res.lines[0].unit_price_minor, 123450);
});

test('AI tenant mismatch blocks review', () => {
  const req = request();
  const aiProposal = { tenant_id: 'ANOTHER-TENANT', model_id: 'MOCK-MODEL', prompt_version: '1',
    reviewed_evidence_ref: 'E-01', product_intents: [] };
  assert.ok(composeDraft(req, { aiProposal }).release_blockers.includes('AI_TENANT_MISMATCH'));
});

test('unapproved source price cannot enter computation', () => {
  const req = request(); req.lines[0].price_status = 'DRAFT';
  assert.throws(() => composeDraft(req), e => e instanceof ContractError && e.code.startsWith('PRICE_NOT_APPROVED'));
});

test('reject mix of cash sale and monthly billing', () => {
  const req = request(); req.lines[0].basis = 'FIXED_MONTHLY';
  assert.throws(() => composeDraft(req), e => e.code === 'CASH_BASIS_INVALID');
});

test('negative and fractional prices fail closed', () => {
  const req = request(); req.lines[0].unit_price_minor = 123.45;
  assert.throws(() => composeDraft(req), e => e.code.startsWith('PRICE_MINOR_INVALID'));
});

test('invalid calendar date fails closed', () => {
  const req = request(); req.valid_until = '2026-02-31';
  assert.throws(() => composeDraft(req), e => e.code === 'VALID_UNTIL_INVALID');
});

test('identical inputs produce identical stable preview IDs across key ordering', () => {
  const req = request();
  const reordered = Object.fromEntries(Object.entries(req).reverse());
  assert.equal(composeDraft(req).draft_id, composeDraft(reordered).draft_id);
});

test('AI processing requires affirmative data-use approval and approved adapter', async () => {
  await assert.rejects(() => interpretRequirements({ brief: 'Two excavators', tenantId: 'SYN',
    allowedProducts: [], modelAdapter: { propose: async () => ({}) } }), /AI_DATA_PROCESSING_APPROVAL_REQUIRED/);
  await assert.rejects(() => interpretRequirements({ brief: 'Two excavators', tenantId: 'SYN',
    allowedProducts: [], personalDataApproved: true }), /AI_ADAPTER_NOT_BOUND/);
});

test('AI adapter receives only allowed product IDs and has no pricing authority', async () => {
  let sent;
  const output = await interpretRequirements({ brief: '2 machines', tenantId: 'SYN',
    personalDataApproved: true, allowedProducts: [{ product_id: 'SYN-01', sensitive: 'NOT_SENT' }],
    modelAdapter: { propose: async input => { sent = input; return { product_intents: [] }; } } });
  assert.deepEqual(sent.product_identifiers, ['SYN-01']);
  assert.equal(sent.task, 'EXTRACT_QUOTE_INTENT_ONLY');
  assert.equal(output.product_intents.length, 0);
});
