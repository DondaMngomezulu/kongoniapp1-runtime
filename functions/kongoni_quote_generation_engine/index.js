'use strict';
// Catalyst Node 20 Advanced I/O, raw http request/response. No CRM writes, email or release.
const catalyst = require('zcatalyst-sdk-node');
const { composeDraft, ContractError } = require('./lib/engine.cjs');
function send(res, status, value) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' });
  res.end(JSON.stringify(value));
}
async function readJSON(req) {
  let text = '';
  for await (const chunk of req) {
    text += chunk.toString('utf8');
    if (Buffer.byteLength(text) > 262144) throw new ContractError('PAYLOAD_TOO_LARGE');
  }
  try { return JSON.parse(text); } catch (_) { throw new ContractError('JSON_INVALID'); }
}
module.exports = async (req, res) => {
  if (process.env.QUOTE_ENGINE_EXECUTION_ENV !== 'Development' ||
      process.env.QUOTE_ENGINE_PREVIEW_ENABLED !== 'true') {
    return send(res, 503, { engine: 'ENG-S01-QUOTATION', status: 'DISABLED',
      reason: 'Development preview requires explicit administrator activation' });
  }
  let user;
  try {
    const app = catalyst.initialize(req);
    user = await app.userManagement().getCurrentUser();
  } catch (_) {
    return send(res, 401, { error: 'AUTHENTICATION_REQUIRED' });
  }
  const permitted = (process.env.QUOTE_ENGINE_DEV_USERS || '').split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
  if (!permitted.length || !user || !permitted.includes(String(user.email_id || user.content?.email_id || '').toLowerCase())) {
    return send(res, 403, { error: 'AUTHORISATION_REQUIRED' });
  }
  const path = new URL(req.url, 'https://localhost').pathname.replace(/\/$/, '');
  if (req.method === 'GET' && path.endsWith('/health')) {
    return send(res, 200, { engine: 'ENG-S01-QUOTATION', status: 'DEVELOPMENT_PREVIEW',
      crm_write_enabled: false, outbound_issue_enabled: false, ai_adapter_connected: false });
  }
  if (req.method !== 'POST' || !path.endsWith('/preview')) return send(res, 404, { error: 'NOT_FOUND' });
  try {
    const data = await readJSON(req);
    // No trusted CRM read adapter wired yet. Caller data is always unverified regardless of flags.
    const draft = composeDraft(data.quote_request, { sourceVerified: false,
      aiProposal: data.ai_proposal || null });
    return send(res, 200, draft);
  } catch (error) {
    const code = error instanceof ContractError ? 422 : 500;
    return send(res, code, { error: error.code || 'ENGINE_FAILURE' });
  }
};
