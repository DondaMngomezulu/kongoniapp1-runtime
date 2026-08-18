"use strict";

const crypto = require("crypto");

function json(res, status, body) {
  res.status(status);
  res.setHeader("content-type", "application/json");
  res.send(JSON.stringify(body));
}

function makeDecisionId(requestId) {
  return `TAXDEC-${crypto.createHash("sha256").update(String(requestId)).digest("hex").slice(0, 16)}`;
}

function validateContext(body) {
  const required = ["request_id", "legal_entity_id", "event_type", "event_date", "jurisdiction", "amount", "currency"];
  const missing = required.filter((k) => body[k] === undefined || body[k] === null || body[k] === "");
  if (missing.length) return [`Missing required fields: ${missing.join(", ")}`];
  if (body.jurisdiction !== "ZA") return ["MS-GC-TAX-001 currently supports jurisdiction ZA only."];
  if (!/^[A-Z]{3}$/.test(String(body.currency))) return ["currency must be a 3-letter uppercase ISO-style code."];
  return [];
}

function approvedRulesAvailable() {
  // Controlled scaffold: no embedded SARS rule logic is permitted.
  // Replace only with governed REG-SARS-RULE-001 retrieval after approved atomic rules exist.
  return false;
}

module.exports = async (req, res) => {
  const correlationId = req.getHeader?.("x-correlation-id") || req.headers?.["x-correlation-id"] || crypto.randomUUID();
  try {
    if (req.method !== "POST") {
      return json(res, 405, { error: "METHOD_NOT_ALLOWED", correlation_id: correlationId });
    }

    let body = req.body;
    if (typeof body === "string") body = JSON.parse(body || "{}");
    body = body || {};

    const errors = validateContext(body);
    if (errors.length) {
      return json(res, 400, {
        decision_id: makeDecisionId(body.request_id || correlationId),
        request_id: body.request_id || correlationId,
        status: "ERROR",
        posting_authorised: false,
        applicable_tax_domains: [],
        obligations: [],
        rule_evidence: [],
        errors,
        correlation_id: correlationId
      });
    }

    if (!approvedRulesAvailable()) {
      return json(res, 409, {
        decision_id: makeDecisionId(body.request_id),
        request_id: body.request_id,
        status: "PENDING_RULES",
        posting_authorised: false,
        applicable_tax_domains: [],
        obligations: [],
        rule_evidence: [],
        errors: ["No approved atomic SARS rule set is bound to MS-GC-TAX-001. Service fails closed."],
        correlation_id: correlationId
      });
    }

    return json(res, 501, {
      decision_id: makeDecisionId(body.request_id),
      request_id: body.request_id,
      status: "ERROR",
      posting_authorised: false,
      applicable_tax_domains: [],
      obligations: [],
      rule_evidence: [],
      errors: ["Approved rule execution engine is not implemented in this scaffold."],
      correlation_id: correlationId
    });
  } catch (err) {
    return json(res, 500, {
      status: "ERROR",
      posting_authorised: false,
      rule_evidence: [],
      errors: [err.message || "Unhandled error"],
      correlation_id: correlationId
    });
  }
};
