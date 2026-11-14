'use strict';
// CRM is the authoritative quote transaction store. This is a *candidate*, not an API write.
function crmDraftCandidate(request, result) {
  return {
    integration_state: 'NOT_WRITE_READY',
    reason: 'Quoted_Items subform/line-item field contract and managed CRM connection require verification',
    allowed_write_mode: 'NONE',
    module: 'Quotes',
    header: {
      Subject: request.subject,
      Deal_Name: { id: request.deal_id },
      Account_Name: { id: request.account_id },
      Quote_Date: request.quote_date,
      Valid_Till: request.valid_until,
      Quote_Stage: 'Draft',
      Quote_State: 'inProgress',
      Release_Status: 'Pending'
    },
    proposed_line_items: result.lines.map(x => ({ product_id: x.product_id, quantity: x.quantity,
      billing_basis: x.basis, unit_price_minor: x.unit_price_minor,
      planned_hours_per_unit: x.planned_hours_per_unit,
      price_source_ref: x.price_source_ref })),
    pricing_summary_minor: result.totals,
    source_request_id: request.request_id,
    document_template_id: request.provenance.document_template_id,
    approved_for_customer_issue: false
  };
}
module.exports = { crmDraftCandidate };
