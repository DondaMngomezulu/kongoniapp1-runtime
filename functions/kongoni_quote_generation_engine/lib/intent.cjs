'use strict';
// Untrusted model suggestions must never become price, tax, release or legal authorities.
function assessAIProposal(proposal, request) {
  if (proposal == null) return { present: false, model_id: null, candidates: [], blocks: [] };
  const blocks = [];
  if (typeof proposal !== 'object' || Array.isArray(proposal)) {
    return { present: true, model_id: null, candidates: [], blocks: ['AI_PROPOSAL_INVALID'] };
  }
  const forbidden = ['prices', 'price', 'tax_rate_bps', 'credit_approved', 'release_approved',
    'approved_terms', 'discount', 'unit_price_minor', 'crm_write_authorised'];
  if (forbidden.some(k => Object.prototype.hasOwnProperty.call(proposal, k))) blocks.push('AI_AUTHORITY_OVERRIDE_REJECTED');
  if (proposal.tenant_id !== request.tenant_id) blocks.push('AI_TENANT_MISMATCH');
  if (!proposal.model_id || !proposal.prompt_version || !proposal.reviewed_evidence_ref) {
    blocks.push('AI_PROVENANCE_MISSING');
  }
  const candidates = [];
  if (!Array.isArray(proposal.product_intents) || proposal.product_intents.length > 100) {
    blocks.push('AI_LINES_INVALID');
  } else {
    for (const item of proposal.product_intents) {
      if (!item || typeof item !== 'object' || !Number.isSafeInteger(item.quantity) || item.quantity < 1 ||
          !item.evidence_ref || !request.lines.some(l => l.product_id === item.product_id && l.quantity === item.quantity)) {
        blocks.push('AI_PRODUCT_OR_QUANTITY_UNVERIFIED');
        continue;
      }
      if (forbidden.some(k => Object.prototype.hasOwnProperty.call(item, k))) {
        blocks.push('AI_AUTHORITY_OVERRIDE_REJECTED');
      }
      candidates.push({ product_id: item.product_id, quantity: item.quantity,
        evidence_ref: String(item.evidence_ref) });
    }
  }
  return { present: true, model_id: proposal.model_id || null, candidates,
    blocks: Array.from(new Set(blocks)) };
}
async function interpretRequirements({ brief, allowedProducts, tenantId, modelAdapter,
  personalDataApproved = false }) {
  if (!personalDataApproved) throw new Error('AI_DATA_PROCESSING_APPROVAL_REQUIRED');
  if (!modelAdapter || typeof modelAdapter.propose !== 'function') throw new Error('AI_ADAPTER_NOT_BOUND');
  if (typeof brief !== 'string' || brief.length > 5000 || !brief.trim()) throw new Error('BRIEF_INVALID');
  if (!Array.isArray(allowedProducts) || allowedProducts.length > 200) throw new Error('CATALOGUE_INVALID');
  // The supplied provider is an *approved* model adapter, not a provider selected by AI.
  const suggestion = await modelAdapter.propose({ tenant_id: tenantId, task: 'EXTRACT_QUOTE_INTENT_ONLY',
    text: brief, product_identifiers: allowedProducts.map(x => x.product_id),
    prohibited: ['pricing', 'taxation', 'discounts', 'release', 'legal conclusions'] });
  return suggestion; // assessAIProposal must validate it before use.
}
module.exports = { assessAIProposal, interpretRequirements };
