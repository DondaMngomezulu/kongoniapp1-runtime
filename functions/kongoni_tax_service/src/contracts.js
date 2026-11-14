'use strict';

const APQC_ACTIVITIES = new Set([
  '9.9.1.1', '9.9.1.2', '9.9.1.3', '9.9.2.1', '9.9.2.2',
  '9.9.2.3', '9.9.2.4', '9.9.2.5', '9.9.2.6', '9.9.2.7'
]);

const TAX_TYPES = new Set([
  'VAT', 'CORPORATE_INCOME_TAX', 'CAPITAL_GAINS_TAX', 'DEFERRED_TAX',
  'WITHHOLDING_TAX', 'PAYROLL_TAX', 'CUSTOMS_EXCISE', 'OTHER'
]);

function isDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const date = new Date(`${value}T00:00:00.000Z`);
  return Number.isFinite(date.valueOf()) && date.toISOString().slice(0, 10) === value;
}

function validateEvaluationCommand(command) {
  const errors = [];
  if (!command || typeof command !== 'object' || Array.isArray(command)) {
    return ['body must be a JSON object'];
  }

  for (const name of ['requestId', 'entityId', 'ruleId']) {
    if (typeof command[name] !== 'string' || command[name].trim() === '') {
      errors.push(`${name} is required`);
    }
  }
  if (!isDate(command.asOfDate)) errors.push('asOfDate must use YYYY-MM-DD');
  if (!APQC_ACTIVITIES.has(command.apqcActivity)) errors.push('apqcActivity is outside APQC 9.9 Level 4 scope');
  if (!TAX_TYPES.has(command.taxType)) errors.push('taxType is not supported');
  if (!command.facts || typeof command.facts !== 'object' || Array.isArray(command.facts)) {
    errors.push('facts must be a JSON object');
  }
  return errors;
}

module.exports = { APQC_ACTIVITIES, TAX_TYPES, isDate, validateEvaluationCommand };

