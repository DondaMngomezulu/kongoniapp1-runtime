'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { handleSignal } = require('../src/handler');

function envelope(overrides = {}) {
  return {
    account: {
      project: {
        id: '86824000000020001',
        environment: 'Development'
      }
    },
    events: [{
      event_config: { api_name: 'kongoni_tax_evaluation_requested_v1' },
      data: {
        eventType: 'kongoni.tax.evaluation.requested.v1',
        eventId: 'EVT-001',
        occurredAt: '2026-08-20T08:00:00Z',
        source: 'chatgpt',
        schemaVersion: '1.0.0',
        correlationId: 'REQ-001',
        idempotencyKey: 'EVT-001',
        data: {
          requestId: 'REQ-001',
          entityId: 'ENTITY-001',
          asOfDate: '2026-08-20',
          apqcActivity: '9.9.2.1',
          taxType: 'CORPORATE_INCOME_TAX',
          ruleId: 'GR-SARS-TAX-001',
          facts: { baseAmountMinor: '10000' }
        }
      }
    }],
    ...overrides
  };
}

function successfulFetch(calls) {
  return async (url, options) => {
    calls.push({ url, options });
    return {
      ok: true,
      status: 200,
      async json() {
        return { decision: 'REVIEW_REQUIRED', postingStatus: 'POSTING_BLOCKED' };
      }
    };
  };
}

test('a valid Development event is sent to the tax service', async () => {
  const calls = [];
  const result = await handleSignal(envelope(), {
    serviceUrl: 'https://development.example.invalid/tax/',
    serviceToken: 'test-token-not-a-secret',
    fetchImpl: successfulFetch(calls)
  });
  assert.equal(result.processed, 1);
  assert.equal(result.results[0].decision, 'REVIEW_REQUIRED');
  assert.equal(calls[0].url, 'https://development.example.invalid/tax/v1/evaluations');
  assert.equal(calls[0].options.headers['idempotency-key'], 'EVT-001');
});

test('a Production event is blocked', async () => {
  const input = envelope();
  input.account.project.environment = 'Production';
  await assert.rejects(
    handleSignal(input, { serviceUrl: 'https://example.invalid', serviceToken: 'test-token', fetchImpl: async () => {} }),
    /Only the Development environment is authorized/
  );
});

test('an event from another project is blocked', async () => {
  const input = envelope();
  input.account.project.id = 'OTHER';
  await assert.rejects(
    handleSignal(input, { serviceUrl: 'https://example.invalid', serviceToken: 'test-token', fetchImpl: async () => {} }),
    /Signal project is not authorized/
  );
});

test('an unsupported event contract is blocked', async () => {
  const input = envelope();
  input.events[0].data.schemaVersion = '2.0.0';
  await assert.rejects(
    handleSignal(input, { serviceUrl: 'https://example.invalid', serviceToken: 'test-token', fetchImpl: async () => {} }),
    /Signal event contract is not supported/
  );
});

test('an insecure service URL is blocked', async () => {
  await assert.rejects(
    handleSignal(envelope(), { serviceUrl: 'http://example.invalid', serviceToken: 'test-token', fetchImpl: async () => {} }),
    /must use HTTPS/
  );
});

test('a missing service token is blocked', async () => {
  await assert.rejects(
    handleSignal(envelope(), { serviceUrl: 'https://example.invalid', fetchImpl: async () => {} }),
    /KONGONI_TAX_SERVICE_TOKEN is required/
  );
});

test('an invalid tax-service response is blocked', async () => {
  const fetchImpl = async () => ({
    ok: true,
    status: 200,
    async json() { return { decision: 'UNKNOWN' }; }
  });
  await assert.rejects(
    handleSignal(envelope(), { serviceUrl: 'https://example.invalid', serviceToken: 'test-token', fetchImpl }),
    /invalid decision contract/
  );
});
