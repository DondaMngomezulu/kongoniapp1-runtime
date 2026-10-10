'use strict';

const { isDate } = require('./contracts');

function decisionIsEffective(decision, asOfDate) {
  return decision &&
    decision.decision === 'VALID' &&
    typeof decision.evidenceId === 'string' && decision.evidenceId.length > 0 &&
    isDate(decision.effectiveFrom) &&
    asOfDate >= decision.effectiveFrom &&
    (!decision.effectiveTo || (isDate(decision.effectiveTo) && asOfDate <= decision.effectiveTo));
}

function validatePosting(command) {
  if (!command || typeof command !== 'object' || !command.requestId || !isDate(command.asOfDate)) {
    return {
      httpStatus: 400,
      body: { error: 'INVALID_COMMAND', message: 'requestId and asOfDate are required.' }
    };
  }

  const sarsValid = decisionIsEffective(command.sarsDecision, command.asOfDate);
  const ifrsValid = decisionIsEffective(command.ifrsDecision, command.asOfDate);
  const reasons = [];
  if (!sarsValid) reasons.push('SARS_DECISION_INVALID_OR_INEFFECTIVE');
  if (!ifrsValid) reasons.push('IFRS_DECISION_INVALID_OR_INEFFECTIVE');

  return {
    httpStatus: 200,
    body: {
      requestId: command.requestId,
      decision: reasons.length === 0 ? 'POSTING_ALLOWED' : 'POSTING_BLOCKED',
      reasons,
      apqcActivity: '9.9.2.5',
      controlId: 'CTL-IAS12-DT-001'
    }
  };
}

module.exports = { decisionIsEffective, validatePosting };

