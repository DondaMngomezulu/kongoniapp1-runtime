'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { composeFromCrm, cents, getBasis, validateSelection, createCrmReader } = require('../lib/crm-source.cjs');
const { templateFor, inspectTemplate } = require('../lib/templates.cjs');
const fakeId = n => String(5643538000000000000n + BigInt(n));
const ids = { deal: fakeId(11), account: fakeId(12), product: fakeId(13), price: fakeId(14),
  offering: fakeId(15), template: templateFor('CASH_SALE').id };
function req() {
  return { schema_version: '1.0', request_id: 'TEST-CRMLIVE-1', tenant_id: 'TEST',
    deal_id: ids.deal, account_id: ids.account, quote_type: 'CASH_SALE',
    subject: 'SANDBOX CASH QUOTE', quote_date: '2026-10-09', valid_until: '2026-10-20',
    line_selections: [{ line_id: 'L1', product_id: ids.product, offering_price_id: ids.price, quantity: 2 }] };
}
const profile = { approval_status: 'APPROVED', rate_bps: 1500,
  source_ref: 'VAT-RULE-TEST-2026', policy_version: 'TEST-1', valid_from: '2026-01-01' };
function source(opts = {}) {
  const data = {
    Deals: { id: ids.deal, Account_Name: { id: ids.account } },
    Accounts: { id: ids.account, Account_Name: 'Synthetic Example' },
    Products: { id: ids.product, Lifecycle_Status: 'Active', Product_Use_Status: 'Approved' },
    ProductOfferingPrices: { id: ids.price, Transactional_Product: { id: ids.product },
      Product_Offering: { id: ids.offering }, Price_Status: 'Approved', Currency: 'ZAR',
      Unit_Price: '1000.25', Price_Type: 'One Time', Price_ID: 'P-1',
      Price_Source_ID: 'SRC-TEST-1', Evidence_Reference: 'SYNTHETIC-EVIDENCE',
      Authority_Reference: 'SYNTHETIC-AUTHORITY', Pricing_Rule_ID: 'TEST-POLICY',
      Effective_From: '2026-01-01' },
    ProductOfferings: { id: ids.offering, Transactional_Product: { id: ids.product },
      Offering_Status: 'Active', Terms_Status: 'Approved', Terms_Approved: true }
  };
  for (const [k, v] of Object.entries(opts)) if (k !== 'template') Object.assign(data[k], v);
  const template = { id: ids.template, name: 'Cash', primary_module: { api_name: 'Quotes' },
    content: '<div>Quotes.Quoted_Items Quotes.Quote_Number Quotes.Account_Name</div>' };
  return { getRecord: async (module, id) => {
    if (!data[module] || data[module].id !== id) throw Error('Bad synthetic ID');
    return data[module]; },
    getTemplate: async () => opts.template || template
  };
}
test('exact decimal currency parsing from CRM', () => {
  assert.equal(cents('1.23'), 123);
  assert.equal(cents(1000.25), 100025);
  assert.throws(() => cents(10.999), /CRM_CURRENCY_PRECISION_INVALID/);
});
test('approval gated CRM draft cannot send or write', async () => {
  const out = await composeFromCrm(source(), req(), { tenantId: 'TEST', taxProfile: profile });
  assert.equal(out.totals.ONE_TIME.ex_tax_minor, 200050);
  assert.equal(out.totals.ONE_TIME.tax_minor, 30008);
  assert.equal(out.customer_issue_authorised, false);
  assert.equal(out.crm_write_authorised, false);
  assert.equal(out.crm_draft_candidate.native_line_candidate[0].List_Price, 1000.25);
  assert.equal(out.review_status, 'HOLD');
  assert.ok(out.release_blockers.some(x => x.includes('stock')));
});
test('cannot obtain price from user overrides', async () => {
  const q=req(); q.line_selections[0].unit_price_minor=1;
  assert.throws(() => validateSelection(q), /LINE_SELECTION_AUTHORITY_OVERRIDE/);
});
test('account and tenant isolation', async () => {
  await assert.rejects(composeFromCrm(source(), req(), { tenantId:'OTHER', taxProfile:profile }), /TENANT_SCOPE_MISMATCH/);
  await assert.rejects(composeFromCrm(source({ Deals: { Account_Name: { id: fakeId(99) } } }), req(),
    { tenantId:'TEST', taxProfile:profile }), /CRM_DEAL_ACCOUNT_MISMATCH/);
});
test('unapproved or mismatched price rejected', async () => {
  await assert.rejects(composeFromCrm(source({ ProductOfferingPrices: { Price_Status:'Draft' } }), req(),
    { tenantId:'TEST', taxProfile:profile }), /PRICE_NOT_APPROVED/);
  await assert.rejects(composeFromCrm(source({ ProductOfferingPrices: { Transactional_Product:{id: fakeId(99)} } }), req(),
    { tenantId:'TEST', taxProfile:profile }), /PRICE_PRODUCT_MISMATCH/);
});
test('customer-specific price cannot leak across accounts', async () => {
  await assert.rejects(composeFromCrm(source({ ProductOfferingPrices: { Customer:{id:fakeId(99)} } }), req(),
    {tenantId:'TEST',taxProfile:profile}), /PRICE_CUSTOMER_MISMATCH/);
});
test('tax policy must be approved, dated and server-trusted', async () => {
  await assert.rejects(composeFromCrm(source(), req(), {tenantId:'TEST'}),
    /TRUSTED_TAX_PROFILE_REQUIRED/);
  await assert.rejects(composeFromCrm(source(), req(), {tenantId:'TEST',
    taxProfile:{...profile,approval_status:'Draft'}}), /TRUSTED_TAX_PROFILE_REQUIRED/);
});
test('approved price without evidence is internally blocked', async () => {
  const out=await composeFromCrm(source({ ProductOfferingPrices: { Evidence_Reference:null } }),req(),
    {tenantId:'TEST',taxProfile:profile});
  assert.ok(out.release_blockers.includes('GATE_NOT_EVIDENCED:pricing'));
});
test('billing basis must be unambiguous', () => {
  assert.equal(getBasis({Price_Type:'One Time',Unit_of_Measure:'EA Each'},'CASH_SALE'),'ONE_TIME');
  assert.equal(getBasis({Price_Type:'Recurring',Unit_of_Measure:'ZAR per unit per month'},'DRY_RENTAL'),'FIXED_MONTHLY');
  assert.equal(getBasis({Price_Type:'Recurring',Unit_of_Measure:'ZAR per hour'},'OPERATING_LEASE'),'HOURLY_VARIABLE');
  assert.throws(()=>getBasis({Price_Type:'Recurring',Unit_of_Measure:'Unit'},'DRY_RENTAL'),/CRM_PRICE_BILLING_BASIS_UNVERIFIED/);
});
test('template fields checked without declaring legal approval', () => {
  const t=templateFor('CASH_SALE');
  const m=inspectTemplate({id:t.id,primary_module:{api_name:'Quotes'},
    content:'Quotes.Quoted_Items Quotes.Quote_Number Quotes.Account_Name'},t);
  assert.equal(m.schema_ok,true);
  assert.equal(m.approval_state,'PENDING_VERIFICATION');
});
test('CRM reader uses managed Zoho OAuth and strict domain validation', async () => {
  let requested;
  const reader=createCrmReader({connections:()=>({getConnectionCredentials:async()=>({
    headers:{Authorization:'Zoho-oauthtoken SYNTHETIC-NOT-SECRET'},
    parameters:{api_domain:'https://www.zohoapis.com'}})})},{
    fetchImpl:async (url,config)=>{requested={url,config};return{ok:true,json:async()=>({data:[{id:ids.account}]})}}
  });
  const acc=await reader.getRecord('Accounts',ids.account);
  assert.equal(acc.id,ids.account);
  assert.ok(requested.url.endsWith('/crm/v8/Accounts/'+ids.account));
  assert.equal(requested.config.method,'GET');
  assert.throws(() => reader.getRecord('Users',ids.account), /CRM_MODULE_NOT_ALLOWED/);
});
