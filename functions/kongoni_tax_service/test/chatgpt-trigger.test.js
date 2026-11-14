'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const {
  classifyTaxIntent,
  prepareTaxEvaluationTrigger
} = require('../src/chatgpt-trigger');

function command(overrides = {}) {
  return {
    requestId: 'REQ-CHAT-001',
    entityId: 'ENTITY-001',
    asOfDate: '2026-08-20',
    apqcActivity: '9.9.2.1',
    taxType: 'CORPORATE_INCOME_TAX',
    ruleId: 'GR-SARS-TAX-001',
    facts: { baseAmountMinor: '10000' },
    ...overrides
  };
}

test('an explicit tax evaluation command matches the trigger', () => {
  assert.equal(classifyTaxIntent('@tax evaluate this transaction'), 'TAX_EVALUATION');
  assert.equal(classifyTaxIntent('Calculate the VAT for this transaction'), 'TAX_EVALUATION');
});

test('a tax information request does not match the action trigger', () => {
  assert.equal(classifyTaxIntent('Explain deferred tax'), 'NO_MATCH');
  assert.equal(classifyTaxIntent('List APQC tax processes'), 'NO_MATCH');
});

test('an incomplete command fails closed and asks for input', () => {
  const result = prepareTaxEvaluationTrigger({
    message: '@tax evaluate',
    command: command({ ruleId: '' }),
    eventIdFactory: () => 'EVT-001'
  });
  assert.equal(result.status, 'INPUT_REQUIRED');
  assert.ok(result.missingOrInvalid.includes('ruleId is required'));
  assert.equal(result.event, undefined);
});

test('a complete command produces the canonical event', () => {
  const result = prepareTaxEvaluationTrigger({
    message: '@tax evaluate',
    command: command(),
    eventIdFactory: () => 'EVT-CHAT-001',
    clock: () => new Date('2026-08-20T08:00:00Z')
  });
  assert.equal(result.status, 'READY');
  assert.equal(result.event.eventType, 'kongoni.tax.evaluation.requested.v1');
  assert.equal(result.event.schemaVersion, '1.0.0');
  assert.equal(result.event.correlationId, 'REQ-CHAT-001');
  assert.equal(result.event.data.ruleId, 'GR-SARS-TAX-001');
});
