'use strict';
const { createHash } = require('node:crypto');
// IDs verified against the live Zoho CRM inventory-template register on 9 October 2026.
// Visibility is not the same as approved contractual wording. Approval remains a separate gate.
const TEMPLATES = Object.freeze({
  CASH_SALE: { id: '5643538000009802330', name: 'VS01-DOC-004 Equipment Cash Sale Quote' },
  OPERATING_LEASE: { id: '5643538000009719005', name: 'VS02-DOC-004 Formal Quote' },
  DRY_RENTAL: { id: '5643538000009719005', name: 'VS02-DOC-004 Formal Quote' }
});
function templateFor(type) {
  if (!Object.prototype.hasOwnProperty.call(TEMPLATES, type)) throw new Error('QUOTE_TEMPLATE_PROFILE_MISSING');
  return TEMPLATES[type];
}
function inspectTemplate(record, binding) {
  const html = record && record.content;
  const moduleName = record && (record.primary_module?.api_name || record.module?.api_name);
  const schemaOk = !!(record && record.id === binding.id && moduleName === 'Quotes' &&
    typeof html === 'string' && html.includes('Quotes.Quoted_Items') &&
    html.includes('Quotes.Quote_Number') && html.includes('Quotes.Account_Name'));
  return {
    id: binding.id, name: binding.name, crm_module: moduleName || null, schema_ok: schemaOk,
    content_sha256: typeof html === 'string' ? createHash('sha256').update(html).digest('hex') : null,
    approval_state: 'PENDING_VERIFICATION',
    output_mechanism: 'Zoho CRM inventory template; no generation or dispatch performed'
  };
}
module.exports = { TEMPLATES, templateFor, inspectTemplate };
