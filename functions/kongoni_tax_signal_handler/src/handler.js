'use strict';

const EXPECTED_PROJECT_ID = '86824000000020001';
const EXPECTED_ENVIRONMENT = 'DEVELOPMENT';
const EXPECTED_EVENT_API_NAME = 'kongoni_tax_evaluation_requested_v1';
const EXPECTED_EVENT_TYPE = 'kongoni.tax.evaluation.requested.v1';
const EXPECTED_SCHEMA_VERSION = '1.0.0';

function parseRawEvent(raw) {
  if (typeof raw === 'string') {
    try {
      return JSON.parse(raw);
    } catch {
      throw new Error('Signal payload must contain valid JSON.');
    }
  }
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
    throw new Error('Signal payload must be a JSON object.');
  }
  return raw;
}

function validateAccount(account) {
  const projectId = String(account?.project?.id || '');
  const environment = String(account?.project?.environment || '').toUpperCase();
  if (projectId !== EXPECTED_PROJECT_ID) {
    throw new Error('Signal project is not authorized.');
  }
  if (environment !== EXPECTED_ENVIRONMENT) {
    throw new Error('Only the Development environment is authorized.');
  }
}

function validateCanonicalEvent(signalEvent) {
  if (signalEvent?.event_config?.api_name !== EXPECTED_EVENT_API_NAME) {
    throw new Error('Signal event API name is not authorized.');
  }

  const event = signalEvent.data;
  if (!event || typeof event !== 'object' || Array.isArray(event)) {
    throw new Error('Signal event data must be a canonical event object.');
  }
  if (event.eventType !== EXPECTED_EVENT_TYPE || event.schemaVersion !== EXPECTED_SCHEMA_VERSION) {
    throw new Error('Signal event contract is not supported.');
  }
  for (const field of ['eventId', 'occurredAt', 'correlationId', 'idempotencyKey']) {
    if (typeof event[field] !== 'string' || event[field].trim() === '') {
      throw new Error(`Signal event ${field} is required.`);
    }
  }
  if (!event.data || typeof event.data !== 'object' || Array.isArray(event.data)) {
    throw new Error('Signal event data.data is required.');
  }
  return event;
}

function normalizeServiceUrl(value) {
  const url = new URL(String(value || ''));
  if (url.protocol !== 'https:') {
    throw new Error('KONGONI_TAX_SERVICE_URL must use HTTPS.');
  }
  return url.toString().replace(/\/$/, '');
}

function requireServiceToken(value) {
  if (typeof value !== 'string' || value.trim() === '') {
    throw new Error('KONGONI_TAX_SERVICE_TOKEN is required.');
  }
  return value;
}

async function postEvaluation(event, { fetchImpl, serviceUrl, serviceToken }) {
  const headers = {
    'content-type': 'application/json',
    'x-correlation-id': event.correlationId,
    'idempotency-key': event.idempotencyKey
  };
  headers.authorization = `Bearer ${serviceToken}`;

  const response = await fetchImpl(`${serviceUrl}/v1/evaluations`, {
    method: 'POST',
    headers,
    body: JSON.stringify(event.data)
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(`Tax service rejected the event with HTTP ${response.status}.`);
  }
  if (!body || !['VALID', 'REVIEW_REQUIRED'].includes(body.decision)) {
    throw new Error('Tax service returned an invalid decision contract.');
  }
  return {
    eventId: event.eventId,
    correlationId: event.correlationId,
    decision: body.decision,
    postingStatus: body.postingStatus
  };
}

async function handleSignal(raw, {
  fetchImpl = globalThis.fetch,
  serviceUrl = process.env.KONGONI_TAX_SERVICE_URL,
  serviceToken = process.env.KONGONI_TAX_SERVICE_TOKEN
} = {}) {
  if (typeof fetchImpl !== 'function') throw new Error('A fetch implementation is required.');
  const envelope = parseRawEvent(raw);
  validateAccount(envelope.account);
  if (!Array.isArray(envelope.events) || envelope.events.length === 0) {
    throw new Error('Signal envelope must contain at least one event.');
  }

  const targetUrl = normalizeServiceUrl(serviceUrl);
  const targetToken = requireServiceToken(serviceToken);
  const results = [];
  for (const signalEvent of envelope.events) {
    const event = validateCanonicalEvent(signalEvent);
    results.push(await postEvaluation(event, {
      fetchImpl,
      serviceUrl: targetUrl,
      serviceToken: targetToken
    }));
  }
  return { processed: results.length, results };
}

module.exports = {
  EXPECTED_ENVIRONMENT,
  EXPECTED_EVENT_API_NAME,
  EXPECTED_EVENT_TYPE,
  EXPECTED_PROJECT_ID,
  EXPECTED_SCHEMA_VERSION,
  handleSignal,
  parseRawEvent,
  requireServiceToken,
  validateCanonicalEvent
};
