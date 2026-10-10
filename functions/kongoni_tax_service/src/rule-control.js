'use strict';

const { isDate } = require('./contracts');

const REQUIRED_AUTHORITY = ['sourceId', 'sourceUri', 'clause'];
const REQUIRED_APPROVAL = ['decisionId', 'approvedAt', 'preparedBy', 'approvedBy', 'approvedByRole'];
const SUPPORTED_METHODS = new Set(['PERCENT_OF_BASE', 'TEMPORARY_DIFFERENCE']);

function assessRule(rule, command) {
  const reasons = [];
  if (!rule) return ['RULE_NOT_FOUND'];
  if (rule.ruleId !== command.ruleId) reasons.push('RULE_ID_MISMATCH');
  if (typeof rule.version !== 'string' || rule.version.length === 0) reasons.push('RULE_VERSION_MISSING');
  if (rule.status !== 'APPROVED_ACTIVE') reasons.push('RULE_NOT_APPROVED_ACTIVE');
  if (!isDate(rule.effectiveFrom)) reasons.push('RULE_EFFECTIVE_FROM_INVALID');
  else if (command.asOfDate < rule.effectiveFrom) reasons.push('RULE_NOT_YET_EFFECTIVE');
  if (rule.effectiveTo && !isDate(rule.effectiveTo)) reasons.push('RULE_EFFECTIVE_TO_INVALID');
  else if (rule.effectiveTo && command.asOfDate > rule.effectiveTo) reasons.push('RULE_EXPIRED');
  if (!SUPPORTED_METHODS.has(rule.method)) reasons.push('RULE_METHOD_UNSUPPORTED');
  if (!Array.isArray(rule.apqcActivities) || !rule.apqcActivities.includes(command.apqcActivity)) {
    reasons.push('RULE_APQC_SCOPE_MISMATCH');
  }
  if (!Array.isArray(rule.taxTypes) || !rule.taxTypes.includes(command.taxType)) {
    reasons.push('RULE_TAX_TYPE_MISMATCH');
  }
  if (!rule.authority || REQUIRED_AUTHORITY.some((name) => !rule.authority[name])) {
    reasons.push('RULE_AUTHORITY_TRACEABILITY_INCOMPLETE');
  }
  if (!rule.approval || REQUIRED_APPROVAL.some((name) => !rule.approval[name])) {
    reasons.push('RULE_APPROVAL_TRACEABILITY_INCOMPLETE');
  } else if (rule.approval.preparedBy === rule.approval.approvedBy) {
    reasons.push('RULE_FOUR_EYES_CONTROL_FAILED');
  }
  return reasons;
}

module.exports = { assessRule };
