'use strict';

const { validateEvaluationCommand } = require('./contracts');

const TAX_EVALUATION_EVENT = 'kongoni.tax.evaluation.requested.v1';
const SCHEMA_VERSION = '1.0.0';

function classifyTaxIntent(message) {
  const text = String(message || '').trim().toLowerCase();
  if (text === '') return 'NO_MATCH';

  if (/^(what|why|when|where|who|explain|describe|list|show|compare|cross[- ]?walk)\b/.test(text)) {
    return 'NO_MATCH';
  }

  if (/^@tax\s+evaluate\b/.test(text)) return 'TAX_EVALUATION';

  const hasTaxObject = /\b(tax|vat|deferred tax|income tax|withholding tax|payroll tax|customs|excise)\b/.test(text);
  const hasEvaluationAction = /\b(calculate|compute|evaluate|assess|determine)\b/.test(text);
  return hasTaxObject && hasEvaluationAction ? 'TAX_EVALUATION' : 'NO_MATCH';
}

function prepareTaxEvaluationTrigger({
  message,
  command,
  eventIdFactory,
  clock = () => new Date()
}) {
  if (classifyTaxIntent(message) !== 'TAX_EVALUATION') {
    return { status: 'NO_MATCH' };
  }

  const validationErrors = validateEvaluationCommand(command);
  if (validationErrors.length > 0) {
    return {
      status: 'INPUT_REQUIRED',
      missingOrInvalid: validationErrors,
      instruction: 'Ask for one missing or invalid field. Do not estimate a tax result.'
    };
  }

  if (typeof eventIdFactory !== 'function') {
    throw new TypeError('eventIdFactory is required.');
  }

  const eventId = eventIdFactory();
  return {
    status: 'READY',
    event: {
      eventType: TAX_EVALUATION_EVENT,
      eventId,
      occurredAt: clock().toISOString(),
      source: 'chatgpt',
      schemaVersion: SCHEMA_VERSION,
      correlationId: command.requestId,
      idempotencyKey: eventId,
      data: command
    }
  };
}

module.exports = {
  SCHEMA_VERSION,
  TAX_EVALUATION_EVENT,
  classifyTaxIntent,
  prepareTaxEvaluationTrigger
};
