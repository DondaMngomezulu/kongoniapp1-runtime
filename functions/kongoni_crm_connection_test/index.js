'use strict';

const catalyst = require('zcatalyst-sdk-node');
const https = require('https');

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(payload));
}

function httpGet(url, headers) {
  return new Promise((resolve, reject) => {
    const request = https.get(url, { headers }, (response) => {
      let body = '';
      response.on('data', (chunk) => { body += chunk; });
      response.on('end', () => {
        let parsed = body;
        try { parsed = body ? JSON.parse(body) : {}; } catch (_) {}
        resolve({ statusCode: response.statusCode, body: parsed });
      });
    });
    request.on('error', reject);
  });
}

module.exports = async (req, res) => {
  if (req.method !== 'GET') {
    return sendJson(res, 405, {
      status: 'failure',
      test: 'zoho_crm_connection_read',
      error: 'METHOD_NOT_ALLOWED'
    });
  }

  try {
    const app = catalyst.initialize(req);
    const parsedUrl = new URL(req.url, `https://${req.headers.host}`);
    const requestedConnection = parsedUrl.searchParams.get('connection');
    const moduleName = parsedUrl.searchParams.get('module') || 'Accounts';

    const connectionName = requestedConnection || process.env.CRM_CONNECTION_LINK_NAME || 'zoho_crm_write';
    const connections = app.connections();
    const credentials = await connections.getConnectionCredentials(connectionName);

    const headers = { ...(credentials.headers || {}) };
    if (!headers.Authorization && credentials.parameters && credentials.parameters.Authorization) {
      headers.Authorization = credentials.parameters.Authorization;
    }

    if (!headers.Authorization) {
      return sendJson(res, 502, {
        status: 'failure',
        test: 'zoho_crm_connection_read',
        connection: connectionName,
        error: 'CONNECTION_RETURNED_NO_AUTHORIZATION_HEADER'
      });
    }

    const apiDomain =
      (credentials.parameters && (credentials.parameters.api_domain || credentials.parameters.apiDomain)) ||
      process.env.ZOHO_CRM_API_DOMAIN ||
      'https://www.zohoapis.com';

    const endpoint = `${String(apiDomain).replace(/\/$/, '')}/crm/v8/${encodeURIComponent(moduleName)}?per_page=1`;
    const crmResponse = await httpGet(endpoint, headers);
    const ok = crmResponse.statusCode >= 200 && crmResponse.statusCode < 300;

    return sendJson(res, ok ? 200 : 502, {
      status: ok ? 'success' : 'failure',
      test: 'zoho_crm_connection_read',
      connection: connectionName,
      module: moduleName,
      crm_http_status: crmResponse.statusCode,
      record_count: ok && Array.isArray(crmResponse.body && crmResponse.body.data)
        ? crmResponse.body.data.length
        : null,
      crm_error: ok ? null : crmResponse.body,
      credential_exposure: false
    });
  } catch (error) {
    return sendJson(res, 500, {
      status: 'failure',
      test: 'zoho_crm_connection_read',
      error: error && error.message ? error.message : String(error),
      credential_exposure: false
    });
  }
};
