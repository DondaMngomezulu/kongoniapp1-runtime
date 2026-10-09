'use strict';
// Read-only CRM source adapter for ENG-S01-QUOTATION; no write, send, release or approval action.
const { composeDraft, ContractError } = require('./engine.cjs');
const { templateFor, inspectTemplate } = require('./templates.cjs');
const MOD = new Set(['Deals', 'Accounts', 'Products', 'ProductOfferings', 'ProductOfferingPrices']);
class SourceError extends ContractError {
  constructor(code) { super(code); this.name = 'SourceError'; }
}
function guard(ok, code) { if (!ok) throw new SourceError(code); }
function crmId(value) {
  guard(typeof value === 'string' && /^[0-9]{10,25}$/.test(value), 'CRM_RECORD_ID_INVALID');
  return value;
}
function cents(value) {
  const s = String(value);
  guard(/^[0-9]+(?:\.[0-9]{1,2})?$/.test(s), 'CRM_CURRENCY_PRECISION_INVALID');
  const parts = s.split('.');
  const n = BigInt(parts[0]) * 100n + BigInt((parts[1] || '').padEnd(2, '0'));
  guard(n <= BigInt(Number.MAX_SAFE_INTEGER), 'CRM_CURRENCY_OVERFLOW');
  return Number(n);
}
function single(response, key) {
  const list = response && response[key];
  guard(Array.isArray(list) && list.length === 1, 'CRM_RECORD_RESPONSE_INVALID');
  return list[0];
}
function connectionDomain(credentials) {
  const p = credentials.parameters || {};
  const domain = String(p.api_domain || p.apiDomain || process.env.ZOHO_CRM_API_DOMAIN || 'https://www.zohoapis.com').replace(/\/$/, '');
  guard(/^https:\/\/www\.zohoapis\.(com|eu|in|com\.au|jp|ca|sa)$/.test(domain), 'CRM_API_DOMAIN_NOT_ALLOWLISTED');
  return domain;
}
function createCrmReader(app, { connectionName = 'zoho_crm_write', fetchImpl = globalThis.fetch } = {}) {
  guard(app && typeof app.connections === 'function', 'CATALYST_CONNECTIONS_NOT_AVAILABLE');
  guard(typeof fetchImpl === 'function', 'HTTP_TRANSPORT_NOT_AVAILABLE');
  let credentialsPromise;
  async function credentials() {
    if (!credentialsPromise) {
      credentialsPromise = app.connections().getConnectionCredentials(connectionName);
    }
    const c = await credentialsPromise;
    const authorization = (c.headers || {}).Authorization || (c.parameters || {}).Authorization;
    guard(typeof authorization === 'string' && /^Zoho-oauthtoken\s+\S+$/i.test(authorization), 'CRM_MANAGED_OAUTH_NOT_VERIFIED');
    return { authorization, domain: connectionDomain(c) };
  }
  async function load(path, key) {
    const c = await credentials();
    const url = c.domain + '/crm/v8/' + path;
    let response;
    try {
      response = await fetchImpl(url, { method: 'GET',
        headers: { Authorization: c.authorization, Accept: 'application/json' },
        signal: AbortSignal.timeout(8000), redirect: 'error' });
    } catch (_) { throw new SourceError('CRM_SOURCE_UNAVAILABLE'); }
    guard(response && response.ok, 'CRM_SOURCE_HTTP_ERROR');
    let body;
    try { body = await response.json(); }
    catch (_) { throw new SourceError('CRM_SOURCE_JSON_INVALID'); }
    return single(body, key);
  }
  return {
    getRecord(module, id) {
      guard(MOD.has(module), 'CRM_MODULE_NOT_ALLOWED');
      return load(module + '/' + crmId(id), 'data');
    },
    getTemplate(id) {
      return load('settings/inventory_templates/' + crmId(id), 'inventory_templates');
    }
  };
}
function approveTax(profile, quoteDate) {
  guard(profile && profile.approval_status === 'APPROVED' &&
    Number.isInteger(profile.rate_bps) && profile.rate_bps >= 0 && profile.rate_bps <= 10000 &&
    typeof profile.source_ref === 'string' && /^[A-Za-z0-9_.:\/-]{3,120}$/.test(profile.source_ref) &&
    typeof profile.policy_version === 'string' && /^[A-Za-z0-9_.:\/-]{1,120}$/.test(profile.policy_version),
    'TRUSTED_TAX_PROFILE_REQUIRED');
  guard(profile.valid_from && profile.valid_from <= quoteDate &&
    (!profile.valid_to || profile.valid_to >= quoteDate), 'TAX_PROFILE_OUTSIDE_EFFECTIVE_PERIOD');
  return profile;
}
function validateSelection(input) {
  guard(input && typeof input === 'object' && !Array.isArray(input), 'CRM_REQUEST_INVALID');
  const keys = new Set(['schema_version', 'request_id', 'tenant_id', 'deal_id', 'account_id',
    'quote_type', 'subject', 'quote_date', 'valid_until', 'line_selections']);
  guard(Object.keys(input).every(k => keys.has(k)), 'CRM_REQUEST_AUTHORITY_OVERRIDE');
  guard(input.schema_version === '1.0', 'SCHEMA_VERSION_UNSUPPORTED');
  crmId(input.deal_id); crmId(input.account_id);
  guard(typeof input.request_id === 'string' && /^[A-Za-z0-9_.:\/-]{1,90}$/.test(input.request_id), 'REQUEST_ID_INVALID');
  guard(typeof input.tenant_id === 'string' && /^[A-Za-z0-9_.:\/-]{1,120}$/.test(input.tenant_id), 'TENANT_ID_INVALID');
  guard(['CASH_SALE', 'OPERATING_LEASE', 'DRY_RENTAL'].includes(input.quote_type), 'QUOTE_TYPE_INVALID');
  guard(Array.isArray(input.line_selections) && input.line_selections.length > 0 && input.line_selections.length <= 30,
    'LINE_SELECTIONS_INVALID');
  const ids = new Set();
  input.line_selections.forEach(x => {
    guard(x && typeof x === 'object' && !Array.isArray(x), 'LINE_SELECTION_INVALID');
    const allowed = new Set(['line_id', 'product_id', 'offering_price_id', 'quantity', 'planned_hours_per_unit']);
    guard(Object.keys(x).every(k => allowed.has(k)), 'LINE_SELECTION_AUTHORITY_OVERRIDE');
    guard(typeof x.line_id === 'string' && /^[A-Za-z0-9_.:\/-]{1,120}$/.test(x.line_id), 'LINE_ID_INVALID');
    guard(!ids.has(x.line_id), 'DUPLICATE_LINE_ID');
    ids.add(x.line_id);
    crmId(x.product_id); crmId(x.offering_price_id);
    guard(Number.isSafeInteger(x.quantity) && x.quantity > 0 && x.quantity <= 100000, 'QUANTITY_INVALID');
  });
  return input;
}
function getBasis(price, type) {
  const pt = String(price.Price_Type || '').toLowerCase().trim();
  const unit = String(price.Unit_of_Measure || '').toLowerCase();
  if (type === 'CASH_SALE' && (pt === 'one time' || pt === 'one-time') &&
      (!unit || /each|unit|once|ea\b/.test(unit))) return 'ONE_TIME';
  if (type !== 'CASH_SALE' && pt === 'recurring') {
    if (/hour/.test(unit) && !/month/.test(unit)) return 'HOURLY_VARIABLE';
    if (/month/.test(unit) && !/hour/.test(unit)) return 'FIXED_MONTHLY';
  }
  throw new SourceError('CRM_PRICE_BILLING_BASIS_UNVERIFIED');
}
function linked(x) { return x && typeof x.id === 'string' ? x.id : null; }
function evidenceKnown(price) {
  return !!(price.Evidence_Reference && price.Authority_Reference &&
    price.Price_Source_ID && !String(price.Price_Source_ID).startsWith('SOURCE_UNKNOWN'));
}
async function composeFromCrm(reader, incoming, options = {}) {
  validateSelection(incoming);
  guard(options.tenantId === incoming.tenant_id, 'TENANT_SCOPE_MISMATCH');
  const tax = approveTax(options.taxProfile, incoming.quote_date);
  guard(reader && typeof reader.getRecord === 'function' && typeof reader.getTemplate === 'function',
    'CRM_READER_REQUIRED');
  const [deal, account] = await Promise.all([
    reader.getRecord('Deals', incoming.deal_id),
    reader.getRecord('Accounts', incoming.account_id)
  ]);
  guard(deal && deal.id === incoming.deal_id && account && account.id === incoming.account_id &&
    linked(deal.Account_Name) === account.id, 'CRM_DEAL_ACCOUNT_MISMATCH');
  const selected = templateFor(incoming.quote_type);
  const template = await reader.getTemplate(selected.id);
  const templateStatus = inspectTemplate(template, selected);
  const lines = [];
  let catalogueOk = true, pricingOk = true, commercialOk = true;
  for (const s of incoming.line_selections) {
    const [price, product] = await Promise.all([
      reader.getRecord('ProductOfferingPrices', s.offering_price_id),
      reader.getRecord('Products', s.product_id)
    ]);
    guard(price && price.id === s.offering_price_id && product && product.id === s.product_id,
      'CRM_SOURCE_ID_MISMATCH');
    guard(linked(price.Transactional_Product) === product.id, 'PRICE_PRODUCT_MISMATCH');
    guard(!price.Customer || linked(price.Customer) === account.id, 'PRICE_CUSTOMER_MISMATCH');
    guard(price.Price_Status === 'Approved', 'PRICE_NOT_APPROVED');
    guard(price.Currency === 'ZAR', 'PRICE_CURRENCY_UNSUPPORTED');
    guard(price.Effective_From && price.Effective_From <= incoming.quote_date &&
      (!price.Effective_To || price.Effective_To >= incoming.quote_date), 'PRICE_NOT_EFFECTIVE');
    const offeringId = linked(price.Product_Offering);
    guard(!!offeringId, 'PRICE_OFFERING_REQUIRED');
    const offering = await reader.getRecord('ProductOfferings', offeringId);
    guard(offering && offering.id === offeringId &&
      linked(offering.Transactional_Product) === product.id, 'OFFERING_PRODUCT_MISMATCH');
    guard(!offering.Customer_Context || linked(offering.Customer_Context) === account.id,
      'OFFERING_CUSTOMER_MISMATCH');
    guard(!offering.Valid_From || offering.Valid_From <= incoming.quote_date, 'OFFERING_NOT_YET_EFFECTIVE');
    guard(!offering.Valid_To || offering.Valid_To >= incoming.quote_date, 'OFFERING_EXPIRED');
    const basis = getBasis(price, incoming.quote_type);
    if (basis === 'HOURLY_VARIABLE') {
      guard(Number.isSafeInteger(s.planned_hours_per_unit) && s.planned_hours_per_unit >= 0,
        'PLANNED_HOURS_REQUIRED');
    } else guard(s.planned_hours_per_unit == null, 'UNEXPECTED_PLANNED_HOURS');
    catalogueOk = catalogueOk && product.Lifecycle_Status === 'Active' &&
      ['Approved', 'Active'].includes(product.Product_Use_Status) &&
      offering.Offering_Status === 'Active';
    pricingOk = pricingOk && evidenceKnown(price) &&
      !!(price.Pricing_Rule_ID || price.Latest_Price_Version_ID);
    commercialOk = commercialOk && offering.Terms_Approved === true &&
      offering.Terms_Status === 'Approved';
    lines.push({
      line_id: s.line_id, product_id: product.id, price_source_ref: price.Price_ID || price.id,
      tax_source_ref: tax.source_ref,
      price_rule_version: price.Latest_Price_Version_ID || price.Pricing_Rule_ID || price.Price_ID || price.id,
      price_status: 'APPROVED', basis, quantity: s.quantity,
      planned_hours_per_unit: basis === 'HOURLY_VARIABLE' ? s.planned_hours_per_unit : null,
      unit_price_minor: cents(price.Unit_Price), tax_rate_bps: tax.rate_bps
    });
  }
  const gates = {
    catalogue: catalogueOk, pricing: pricingOk, tax: true, commercial_terms: commercialOk,
    counterparty: true, stock: false, issuer: false,
    document_template: templateStatus.schema_ok && !!options.templateApprovalRef,
    credit: false, legal: false, lifecycle_cost: false, finance: false
  };
  const gate_evidence = {};
  if (catalogueOk) gate_evidence.catalogue = 'CRM:' + incoming.request_id;
  if (pricingOk) gate_evidence.pricing = 'CRM:ProductOfferingPrices:' + incoming.request_id;
  gate_evidence.tax = tax.source_ref;
  if (commercialOk) gate_evidence.commercial_terms = 'CRM:ProductOfferings:' + incoming.request_id;
  gate_evidence.counterparty = 'CRM:Deals:' + deal.id;
  if (gates.document_template) gate_evidence.document_template = options.templateApprovalRef;
  const request = {
    schema_version: '1.0', request_id: incoming.request_id, tenant_id: incoming.tenant_id,
    deal_id: deal.id, account_id: account.id, quote_type: incoming.quote_type,
    currency: 'ZAR', subject: incoming.subject, quote_date: incoming.quote_date,
    valid_until: incoming.valid_until, lines, gates, gate_evidence,
    provenance: {
      source_system: 'Zoho CRM', snapshot_id: 'CRM-' + incoming.request_id,
      catalogue_version: 'CRM-LIVE', policy_version: tax.policy_version,
      document_template_id: selected.id
    }
  };
  const result = composeDraft(request, { sourceVerified: true });
  result.template_binding = templateStatus;
  result.crm_draft_candidate.integration_state = 'SOURCE_MAPPED_PREVIEW_ONLY';
  result.crm_draft_candidate.allowed_write_mode = 'NONE';
  result.crm_draft_candidate.native_line_candidate = lines.map((x, i) => ({
    Product_Name: { id: x.product_id },
    Quantity: x.quantity,
    List_Price: x.unit_price_minor / 100,
    Offering_Price: { id: incoming.line_selections[i].offering_price_id },
    Description: 'INTERNAL REVIEW ONLY: ' + x.basis +
      (x.basis === 'HOURLY_VARIABLE' ? '; reference hours ' + x.planned_hours_per_unit : ''),
    Pricing_Rule_ID: x.price_rule_version
  }));
  return result;
}
module.exports = { SourceError, createCrmReader, composeFromCrm, cents, validateSelection, getBasis };
