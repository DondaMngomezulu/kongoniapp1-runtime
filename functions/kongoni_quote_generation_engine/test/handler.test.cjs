'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { Readable } = require('node:stream');
const Module = require('node:module');
const originalLoad = Module._load;
let currentUser = { email_id: 'developer@example.test' };
Module._load = function(request, parent, isMain) {
  if (request === 'zcatalyst-sdk-node') return { initialize: () => ({ userManagement: () => ({
    getCurrentUser: async () => currentUser
  }) }) };
  return originalLoad.call(this, request, parent, isMain);
};
const handle = require('../index.js');
Module._load = originalLoad;
async function call(method, url, body) {
  const req = Readable.from(body === undefined ? [] : [JSON.stringify(body)]);
  req.method = method; req.url = url; req.headers = { host: 'example.test' };
  const res = { status: null, body: null,
    writeHead(status) { this.status = status; },
    end(data) { this.body = JSON.parse(data); } };
  await handle(req, res);
  return res;
}
function setEnv() {
  process.env.QUOTE_ENGINE_EXECUTION_ENV = 'Development';
  process.env.QUOTE_ENGINE_PREVIEW_ENABLED = 'true';
  process.env.QUOTE_ENGINE_DEV_USERS = 'developer@example.test';
  currentUser = { email_id: 'developer@example.test' };
}
test('transport denies all operations without explicit Development activation', async () => {
  delete process.env.QUOTE_ENGINE_EXECUTION_ENV;
  delete process.env.QUOTE_ENGINE_PREVIEW_ENABLED;
  const r = await call('GET', '/health');
  assert.equal(r.status, 503); assert.equal(r.body.status, 'DISABLED');
});
test('transport denies a caller not in the approved user allowlist', async () => {
  setEnv(); currentUser = { email_id: 'other@example.test' };
  const r = await call('GET', '/health');
  assert.equal(r.status, 403);
});
test('transport health describes preview-only no-write and no-AI-provider status', async () => {
  setEnv(); const r = await call('GET', '/health');
  assert.equal(r.status, 200);
  assert.equal(r.body.crm_write_enabled, false);
  assert.equal(r.body.outbound_issue_enabled, false);
  assert.equal(r.body.ai_adapter_connected, false);
});
test('transport refuses invalid request instead of creating quote', async () => {
  setEnv(); const r = await call('POST', '/preview', { quote_request: {} });
  assert.equal(r.status, 422);
  assert.equal(r.body.error, 'SCHEMA_VERSION_UNSUPPORTED');
});
