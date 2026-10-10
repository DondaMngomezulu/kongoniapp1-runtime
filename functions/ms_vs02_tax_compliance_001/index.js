'use strict';

const crypto = require('crypto');

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(payload));
}

function decisionId(requestId) {
  return `TAXDEC-${crypto.createHash('sha256').update(String(requestId)).digest('hex').slice(0, 16)}`;
}

function validateContext(body) {
  const required = ['request_id', 'legal_entity_id', 'event_type', 'event_date', 'jurisdiction', 'amount', 'currency'];
  const missing = required.filter((key) => body[key] === undefined || body[key] === null || body[key] === '');
  if (missing.length) return [`Missing required fields: ${missing.join(', ')}`];
  if (body.jurisdiction !== 'ZA') return ['MS-VS02-TAX-COMPLIANCE-001 currently supports jurisdiction ZA only.'];
  if (!/^[A-Z]{3}$/.test(String(body.currency))) return ['currency must be a three-letter uppercase code.'];
  if (Number.isNaN(Number(body.amount))) return ['amount must be numeric.'];
  return [];
}

function approvedRuleRegistryBound() {
  // Controlled scaffold only.
  // Replace with governed REG-SARS-RULE-001 retrieval after approved atomic rules exist.
  return false;
}

module.exports = async (req, res) => {
  const correlationId = req.headers?.['x-correlation-id'] || crypto.randomUUID();

  try {
    if (req.method !== 'POST') {
      return sendJson(res, 405, {
        status: 'ERROR',
        posting_authorised: false,
        error: 'METHOD_NOT_ALLOWED',
        correlation_id: correlationId
      });
    }

    let body = req.body;
    if (typeof body === 'string') body = JSON.parse(body || '{}');
    body = body || {};

    const errors = validateContext(body);
    if (errors.length) {
      return sendJson(res, 400, {
        decision_id: decisionId(body.request_id || correlationId),
        request_id: body.request_id || correlationId,
        status: 'ERROR',
        posting_authorised: false,
        applicable_tax_domains: [],
        obligations: [],
        rule_evidence: [],
        errors,
        correlation_id: correlationId
      });
    }

    if (!approvedRuleRegistryBound()) {
      return sendJson(res, 409, {
        decision_id: decisionId(body.request_id),
        request_id: body.request_id,
        status: 'PENDING_RULES',
        posting_authorised: false,
        applicable_tax_domains: [],
        obligations: [],
        rule_evidence: [],
        errors: ['No approved atomic SARS rule set is bound. Service fails closed.'],
        correlation_id: correlationId
      });
    }

    return sendJson(res, 501, {
      decision_id: decisionId(body.request_id),
      request_id: body.request_id,
      status: 'ERROR',
      posting_authorised: false,
      applicable_tax_domains: [],
      obligations: [],
      rule_evidence: [],
      errors: ['Approved rule execution engine is not implemented in this scaffold.'],
      correlation_id: correlationId
    });
  } catch (error) {
    return sendJson(res, 500, {
      status: 'ERROR',
      posting_authorised: false,
      rule_evidence: [],
      errors: [error.message || 'Unhandled error'],
      correlation_id: correlationId
    });
  }
};
