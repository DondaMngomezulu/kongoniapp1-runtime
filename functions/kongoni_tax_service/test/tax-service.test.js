'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { createApplication } = require('../src/application');
const { InMemoryRuleRepository, UnconfiguredRuleRepository } = require('../src/rule-repository');

function approvedRule(overrides = {}) {
  return {
    ruleId: 'GR-SARS-TAX-TEST-001',
    version: '1.0.0',
    status: 'APPROVED_ACTIVE',
    effectiveFrom: '2026-01-01',
    effectiveTo: null,
    apqcActivities: ['9.9.2.1', '9.9.2.4', '9.9.2.5'],
    taxTypes: ['CORPORATE_INCOME_TAX', 'DEFERRED_TAX'],
    method: 'PERCENT_OF_BASE',
    parameters: { rateBps: 2500 },
    authority: {
      sourceId: 'TEST-AUTHORITY-001',
      sourceUri: 'https://example.invalid/test-authority',
      clause: 'TEST-CLAUSE'
    },
    approval: {
      decisionId: 'TEST-APPROVAL-001',
      approvedAt: '2026-01-01T00:00:00Z',
      preparedBy: 'TEST-PREPARER',
      approvedBy: 'TEST-APPROVER',
      approvedByRole: 'TEST_APPROVER'
    },
    ...overrides
  };
}

function evaluation(overrides = {}) {
  return {
    requestId: 'REQ-001',
    entityId: 'ENTITY-001',
    asOfDate: '2026-08-20',
    apqcActivity: '9.9.2.1',
    taxType: 'CORPORATE_INCOME_TAX',
    ruleId: 'GR-SARS-TAX-TEST-001',
    facts: { baseAmountMinor: '10005' },
    ...overrides
  };
}

test('health reports the fail-closed rule mode', async () => {
  const app = createApplication({
    ruleRepository: new UnconfiguredRuleRepository(),
    clock: () => new Date('2026-08-20T00:00:00Z')
  });
  const response = await app.handle({ method: 'GET', path: '/health' });
  assert.equal(response.statusCode, 200);
  assert.equal(response.body.ruleMode, 'FAIL_CLOSED_UNCONFIGURED');
});

test('an unconfigured repository blocks the decision', async () => {
  const app = createApplication({ ruleRepository: new UnconfiguredRuleRepository() });
  const response = await app.handle({ method: 'POST', path: '/v1/evaluations', body: evaluation() });
  assert.equal(response.body.decision, 'REVIEW_REQUIRED');
  assert.deepEqual(response.body.reasons, ['RULE_NOT_FOUND']);
  assert.equal(response.body.postingStatus, 'POSTING_BLOCKED');
});

test('an approved percentage rule calculates with minor units and basis points', async () => {
  const app = createApplication({ ruleRepository: new InMemoryRuleRepository([approvedRule()]) });
  const response = await app.handle({ method: 'POST', path: '/v1/evaluations', body: evaluation() });
  assert.equal(response.body.decision, 'VALID');
  assert.equal(response.body.calculation.taxAmountMinor, '2501');
  assert.match(response.body.inputHash, /^[a-f0-9]{64}$/);
  assert.equal(response.body.ruleEvidence.authority.clause, 'TEST-CLAUSE');
});

test('an expired rule is not executed', async () => {
  const rule = approvedRule({ effectiveTo: '2026-06-30' });
  const app = createApplication({ ruleRepository: new InMemoryRuleRepository([rule]) });
  const response = await app.handle({ method: 'POST', path: '/v1/evaluations', body: evaluation() });
  assert.equal(response.body.decision, 'REVIEW_REQUIRED');
  assert.ok(response.body.reasons.includes('RULE_EXPIRED'));
});

test('an unapproved rule is not executed', async () => {
  const rule = approvedRule({ status: 'SOURCE_ONLY' });
  const app = createApplication({ ruleRepository: new InMemoryRuleRepository([rule]) });
  const response = await app.handle({ method: 'POST', path: '/v1/evaluations', body: evaluation() });
  assert.ok(response.body.reasons.includes('RULE_NOT_APPROVED_ACTIVE'));
});

test('a rule with incomplete authority traceability is not executed', async () => {
  const rule = approvedRule({ authority: { sourceId: 'TEST-AUTHORITY-001' } });
  const app = createApplication({ ruleRepository: new InMemoryRuleRepository([rule]) });
  const response = await app.handle({ method: 'POST', path: '/v1/evaluations', body: evaluation() });
  assert.ok(response.body.reasons.includes('RULE_AUTHORITY_TRACEABILITY_INCOMPLETE'));
});

test('a rule without maker-checker separation is not executed', async () => {
  const rule = approvedRule({
    approval: {
      decisionId: 'TEST-APPROVAL-001',
      approvedAt: '2026-01-01T00:00:00Z',
      preparedBy: 'TEST-SAME-PERSON',
      approvedBy: 'TEST-SAME-PERSON',
      approvedByRole: 'TEST_APPROVER'
    }
  });
  const app = createApplication({ ruleRepository: new InMemoryRuleRepository([rule]) });
  const response = await app.handle({ method: 'POST', path: '/v1/evaluations', body: evaluation() });
  assert.ok(response.body.reasons.includes('RULE_FOUR_EYES_CONTROL_FAILED'));
});

test('an unsupported governed method is not executed', async () => {
  const rule = approvedRule({ method: 'ARBITRARY_SCRIPT' });
  const app = createApplication({ ruleRepository: new InMemoryRuleRepository([rule]) });
  const response = await app.handle({ method: 'POST', path: '/v1/evaluations', body: evaluation() });
  assert.equal(response.body.decision, 'REVIEW_REQUIRED');
  assert.ok(response.body.reasons.includes('RULE_METHOD_UNSUPPORTED'));
});

test('a temporary difference produces a signed calculation and requires IFRS validation', async () => {
  const rule = approvedRule({ method: 'TEMPORARY_DIFFERENCE' });
  const app = createApplication({ ruleRepository: new InMemoryRuleRepository([rule]) });
  const response = await app.handle({
    method: 'POST',
    path: '/v1/evaluations',
    body: evaluation({
      apqcActivity: '9.9.2.4',
      taxType: 'DEFERRED_TAX',
      facts: { carryingAmountMinor: '100000', taxBaseAmountMinor: '60000' }
    })
  });
  assert.equal(response.body.calculation.temporaryDifferenceMinor, '40000');
  assert.equal(response.body.calculation.taxAmountMinor, '10000');
  assert.equal(response.body.postingStatus, 'IFRS_VALIDATION_REQUIRED');
});

test('the posting gate requires effective SARS and IFRS decisions', async () => {
  const app = createApplication({ ruleRepository: new UnconfiguredRuleRepository() });
  const valid = { decision: 'VALID', evidenceId: 'EVD-001', effectiveFrom: '2026-01-01' };
  const response = await app.handle({
    method: 'POST',
    path: '/v1/posting-validations',
    body: {
      requestId: 'REQ-POST-001',
      asOfDate: '2026-08-20',
      sarsDecision: valid,
      ifrsDecision: valid
    }
  });
  assert.equal(response.body.decision, 'POSTING_ALLOWED');
});

test('the posting gate blocks an invalid IFRS decision', async () => {
  const app = createApplication({ ruleRepository: new UnconfiguredRuleRepository() });
  const response = await app.handle({
    method: 'POST',
    path: '/v1/posting-validations',
    body: {
      requestId: 'REQ-POST-002',
      asOfDate: '2026-08-20',
      sarsDecision: { decision: 'VALID', evidenceId: 'SARS-EVD', effectiveFrom: '2026-01-01' },
      ifrsDecision: { decision: 'REVIEW_REQUIRED', evidenceId: 'IFRS-EVD', effectiveFrom: '2026-01-01' }
    }
  });
  assert.equal(response.body.decision, 'POSTING_BLOCKED');
  assert.deepEqual(response.body.reasons, ['IFRS_DECISION_INVALID_OR_INEFFECTIVE']);
});

test('invalid APQC scope is rejected', async () => {
  const app = createApplication({ ruleRepository: new InMemoryRuleRepository([approvedRule()]) });
  const response = await app.handle({
    method: 'POST',
    path: '/v1/evaluations',
    body: evaluation({ apqcActivity: '9.11.1.1' })
  });
  assert.equal(response.statusCode, 400);
  assert.ok(response.body.details.includes('apqcActivity is outside APQC 9.9 Level 4 scope'));
});

test('payroll tax retains the APQC 9.5.3 boundary', async () => {
  const rule = approvedRule({
    taxTypes: ['PAYROLL_TAX'],
    apqcActivities: ['9.9.2.6']
  });
  const app = createApplication({ ruleRepository: new InMemoryRuleRepository([rule]) });
  const response = await app.handle({
    method: 'POST',
    path: '/v1/evaluations',
    body: evaluation({ taxType: 'PAYROLL_TAX', apqcActivity: '9.9.2.6' })
  });
  assert.equal(response.body.processBoundary.primaryProcess, 'APQC 9.5.3');
  assert.equal(response.body.processBoundary.relationship, 'ADJACENT_PROCESS');
});
