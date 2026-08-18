'use strict';

const express = require('express');
const catalyst = require('zcatalyst-sdk-node');
const https = require('https');

const ARCHITECTURE_ID = 'KEA-MOD-HS-001';
const ARCHITECTURE_VERSION = '0.1';
const ARCHITECTURE_HASH = 'e989c6a984b9ef3d1bcca02e31ceda8b50687124d7cb40c5957c40864f1c7526';
const ENGINE_OWNERSHIP_RULE = 'BR-ENG-VS-OWN-001';
const PROFIT_CENTRE_PROFILE = 'PROFIT_CENTRE';
const CUSTODIAN_AGENT = 'urn:kongoni:agent:catalyst-platform-delivery';
const ENVIRONMENT = 'Development';

const app = express();
app.use(express.json({ limit: '256kb' }));

function safeError(err) {
  return err && err.message ? err.message : String(err);
}

function sqlLiteral(value) {
  return `'${String(value ?? '').replace(/'/g, "''")}'`;
}

async function zcql(catalystApp, query) {
  const result = await catalystApp.zcql().executeZCQLQuery(query);
  return Array.isArray(result) ? result : [];
}

async function one(catalystApp, query) {
  const rows = await zcql(catalystApp, query);
  if (!rows.length) return null;
  const wrapper = rows[0];
  const firstKey = Object.keys(wrapper)[0];
  return firstKey ? wrapper[firstKey] : wrapper;
}

async function loadEnvironmentAuthority(catalystApp) {
  return one(catalystApp,
    `SELECT * FROM EnvironmentExecutionAuthority WHERE environment_name=${sqlLiteral(ENVIRONMENT)} AND platform_project_id='86824000000020001' LIMIT 1`
  );
}

async function loadAgentContract(catalystApp, agentUrn) {
  return one(catalystApp,
    `SELECT * FROM AgentContract WHERE agent_urn=${sqlLiteral(agentUrn)} AND active_flag=true AND approval_state='APPROVED' AND lifecycle_state='ACTIVE' LIMIT 1`
  );
}

async function loadToolGovernance(catalystApp, serverName, capabilityGroup) {
  return one(catalystApp,
    `SELECT * FROM MCP_Tool_Register WHERE server_name=${sqlLiteral(serverName)} AND capability_group=${sqlLiteral(capabilityGroup)} LIMIT 1`
  );
}

async function loadArchitectureIndex(catalystApp) {
  return one(catalystApp,
    `SELECT * FROM CatalystRepositoryIndex WHERE ARTIFACT_ID=${sqlLiteral(ARCHITECTURE_ID)} LIMIT 1`
  );
}

async function loadEngine(catalystApp, engineCode) {
  return one(catalystApp,
    `SELECT * FROM EnterpriseEngineCatalog WHERE engine_code=${sqlLiteral(engineCode)} LIMIT 1`
  );
}

async function loadValueStream(catalystApp, valueStreamId) {
  return one(catalystApp,
    `SELECT * FROM EnterpriseValueStream WHERE value_stream_id=${sqlLiteral(valueStreamId)} LIMIT 1`
  );
}

async function resolveEngineValueStream(catalystApp, engineCode) {
  if (!engineCode) return { ok:false, reason:'ENGINE_CODE_REQUIRED' };
  const engine = await loadEngine(catalystApp, engineCode);
  if (!engine) return { ok:false, reason:'ENGINE_NOT_REGISTERED' };
  const valueStreamId = engine.primary_value_stream_id;
  if (!valueStreamId) return { ok:false, reason:'ENGINE_PRIMARY_VALUE_STREAM_REQUIRED' };
  const valueStream = await loadValueStream(catalystApp, valueStreamId);
  if (!valueStream) return { ok:false, reason:'ENGINE_VALUE_STREAM_NOT_FOUND' };
  if (!valueStream.active_flag || String(valueStream.lifecycle_status || '').toUpperCase() !== 'APPROVED_ACTIVE') {
    return { ok:false, reason:'ENGINE_VALUE_STREAM_NOT_ACTIVE' };
  }
  if (String(valueStream.economic_profile_id || '').toUpperCase() !== PROFIT_CENTRE_PROFILE) {
    return { ok:false, reason:'ENGINE_VALUE_STREAM_NOT_PROFIT_CENTRE' };
  }
  return { ok:true, engine, value_stream:valueStream };
}

async function loadPreflight(catalystApp, rowid) {
  return one(catalystApp,
    `SELECT * FROM MCP_Governance_Log WHERE ROWID=${sqlLiteral(rowid)} LIMIT 1`
  );
}

async function logPreflight(catalystApp, p) {
  const now = new Date().toISOString().slice(0, 19).replace('T', ' ');
  const query = `INSERT INTO MCP_Governance_Log (` +
    `event_date,event_type,description,actor,outcome,architecture_id,architecture_version,architecture_hash,server_name,tool_or_capability,task_class,conformance_decision,approval_ref` +
    `) VALUES (` +
    `${sqlLiteral(now)},'Preflight',${sqlLiteral(p.description)},${sqlLiteral(p.actor)},${sqlLiteral(p.outcome)},${sqlLiteral(ARCHITECTURE_ID)},${sqlLiteral(ARCHITECTURE_VERSION)},${sqlLiteral(ARCHITECTURE_HASH)},${sqlLiteral(p.server_name)},${sqlLiteral(p.tool_or_capability)},${sqlLiteral(p.task_class)},${sqlLiteral(p.conformance_decision)},${sqlLiteral(p.approval_ref || '')})`;
  const rows = await zcql(catalystApp, query);
  const wrapper = rows && rows[0] ? rows[0] : null;
  if (!wrapper) return null;
  const k = Object.keys(wrapper)[0];
  const r = k ? wrapper[k] : wrapper;
  return r && r.ROWID ? String(r.ROWID) : null;
}

function contractAllows(contract, serverName) {
  if (!contract || !contract.allowed_tools_json) return false;
  const text = String(contract.allowed_tools_json);
  if (serverName === 'Zoho_Catalyst') return text.includes('catalyst');
  if (serverName === 'Zoho_CRM') return text.includes('crm') || text.includes('catalyst');
  return true;
}

function httpGet(url, headers) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, { headers }, (response) => {
      let body = '';
      response.on('data', c => body += c);
      response.on('end', () => {
        let parsed = body;
        try { parsed = body ? JSON.parse(body) : {}; } catch (_) {}
        resolve({ statusCode: response.statusCode, body: parsed });
      });
    });
    req.on('error', reject);
  });
}

function authHeaders(credentials) {
  const headers = { ...(credentials && credentials.headers ? credentials.headers : {}) };
  if (!headers.Authorization && credentials && credentials.parameters && credentials.parameters.Authorization) {
    headers.Authorization = credentials.parameters.Authorization;
  }
  if (!headers.Authorization && credentials && credentials.access_token) {
    headers.Authorization = `Zoho-oauthtoken ${credentials.access_token}`;
  }
  return headers;
}

app.get('/health', (_req, res) => {
  res.status(200).json({
    status: 'ok',
    service: 'kongoni_mcp_execution_gateway',
    environment: ENVIRONMENT,
    architecture_id: ARCHITECTURE_ID,
    engine_ownership_rule: ENGINE_OWNERSHIP_RULE
  });
});

app.post('/v1/preflight', async (req, res) => {
  try {
    const catalystApp = catalyst.initialize(req, { scope: 'admin' });
    const b = req.body || {};
    const required = ['agent_urn','coordinator_class','server_name','capability_group','operation_type','task_class','environment','request_summary'];
    const missing = required.filter(k => !b[k]);
    if (missing.length) return res.status(400).json({ status:'HOLD', reason:'MISSING_REQUIRED_FIELDS', fields:missing });
    if (b.environment !== ENVIRONMENT) return res.status(403).json({ status:'HOLD', reason:'ENVIRONMENT_NOT_AUTHORISED' });

    const authority = await loadEnvironmentAuthority(catalystApp);
    if (!authority || !authority.active_flag || !authority.architecture_preflight_required || !authority.mcp_gateway_required || authority.coordinator_direct_mutation_allowed) {
      return res.status(403).json({ status:'HOLD', reason:'ENVIRONMENT_AUTHORITY_FAILED' });
    }
    if (String(authority.custodian_agent_urn) !== CUSTODIAN_AGENT) {
      return res.status(403).json({ status:'HOLD', reason:'CUSTODIAN_MISMATCH' });
    }

    const contract = await loadAgentContract(catalystApp, b.agent_urn);
    if (!contract) return res.status(403).json({ status:'HOLD', reason:'NO_ACTIVE_APPROVED_AGENT_CONTRACT' });

    const tool = await loadToolGovernance(catalystApp, b.server_name, b.capability_group);
    if (!tool) return res.status(403).json({ status:'HOLD', reason:'UNREGISTERED_CAPABILITY' });
    if (!tool.approved_for_use || tool.enforcement_mode === 'HARD_BLOCKED') {
      return res.status(403).json({ status:'HOLD', reason:'CAPABILITY_HARD_BLOCKED' });
    }
    if (tool.architecture_preflight_required && (!tool.gateway_required || tool.enforcement_mode !== 'GATEWAY_REQUIRED')) {
      return res.status(403).json({ status:'HOLD', reason:'GATEWAY_CONTROL_MISCONFIGURED' });
    }
    if (!contractAllows(contract, b.server_name)) {
      return res.status(403).json({ status:'HOLD', reason:'AGENT_CONTRACT_TOOL_SCOPE_FAILED' });
    }

    const architecture = await loadArchitectureIndex(catalystApp);
    if (!architecture) return res.status(503).json({ status:'HOLD', reason:'ARCHITECTURE_NOT_AVAILABLE' });
    const indexText = JSON.stringify(architecture);
    if (!indexText.includes(ARCHITECTURE_VERSION) || !indexText.includes(ARCHITECTURE_HASH)) {
      return res.status(409).json({ status:'HOLD', reason:'ARCHITECTURE_VERSION_OR_HASH_MISMATCH' });
    }

    const engineScoped = String(b.operation_type).toUpperCase() === 'ENGINE_EXECUTION' || Boolean(b.engine_code);
    let engineContext = null;
    if (engineScoped) {
      engineContext = await resolveEngineValueStream(catalystApp, b.engine_code);
      if (!engineContext.ok) {
        return res.status(403).json({ status:'HOLD', reason:engineContext.reason, control:ENGINE_OWNERSHIP_RULE });
      }
    }

    const material = ['T2','T3'].includes(String(b.task_class).toUpperCase());
    if (material && !b.approval_ref) {
      return res.status(403).json({ status:'HOLD', reason:'APPROVAL_REFERENCE_REQUIRED' });
    }

    const ownerText = engineContext ? ` Engine ${b.engine_code} owner ${engineContext.value_stream.value_stream_id} resolved under ${ENGINE_OWNERSHIP_RULE}.` : '';
    const preflightRowid = await logPreflight(catalystApp, {
      description: `Rule 14 preflight for ${b.server_name} / ${b.capability_group}: ${b.request_summary}.${ownerText}`,
      actor: b.agent_urn,
      outcome: `Architecture, environment authority, agent contract and MCP capability controls passed.${ownerText}`,
      server_name: b.server_name,
      tool_or_capability: b.capability_group,
      task_class: b.task_class,
      conformance_decision: 'CONFORMANT',
      approval_ref: b.approval_ref
    });

    if (!preflightRowid) return res.status(500).json({ status:'HOLD', reason:'PREFLIGHT_EVIDENCE_WRITE_FAILED' });

    res.status(200).json({
      status:'CONFORMANT',
      preflight_rowid:preflightRowid,
      architecture_id:ARCHITECTURE_ID,
      architecture_version:ARCHITECTURE_VERSION,
      architecture_hash:ARCHITECTURE_HASH,
      engine_code: engineContext ? b.engine_code : null,
      primary_value_stream_id: engineContext ? engineContext.value_stream.value_stream_id : null,
      economic_profile_id: engineContext ? engineContext.value_stream.economic_profile_id : null,
      engine_ownership_rule: engineContext ? ENGINE_OWNERSHIP_RULE : null,
      credential_exposure:false
    });
  } catch (err) {
    res.status(500).json({ status:'HOLD', reason:'PREFLIGHT_ERROR', error:safeError(err), credential_exposure:false });
  }
});

app.post('/v1/execute', async (req, res) => {
  try {
    const catalystApp = catalyst.initialize(req, { scope: 'admin' });
    const b = req.body || {};
    if (!b.preflight_rowid || !b.server_name || !b.capability_group || !b.operation_code) {
      return res.status(400).json({ status:'rejected', reason:'MISSING_EXECUTION_FIELDS' });
    }

    const preflight = await loadPreflight(catalystApp, b.preflight_rowid);
    if (!preflight || preflight.conformance_decision !== 'CONFORMANT') {
      return res.status(403).json({ status:'rejected', reason:'INVALID_PREFLIGHT' });
    }
    if (preflight.architecture_id !== ARCHITECTURE_ID || preflight.architecture_version !== ARCHITECTURE_VERSION || preflight.architecture_hash !== ARCHITECTURE_HASH) {
      return res.status(409).json({ status:'rejected', reason:'STALE_ARCHITECTURE_PREFLIGHT' });
    }
    if (preflight.server_name !== b.server_name || preflight.tool_or_capability !== b.capability_group) {
      return res.status(403).json({ status:'rejected', reason:'PREFLIGHT_SCOPE_MISMATCH' });
    }

    if (b.server_name === 'Zoho_CRM' && b.operation_code === 'CRM_ACCOUNT_READ_TEST') {
      const connectionLink = process.env.CRM_CONNECTION_LINK_NAME;
      if (!connectionLink) return res.status(500).json({ status:'failure', reason:'CRM_CONNECTION_LINK_NAME_NOT_CONFIGURED' });
      const credentials = await catalystApp.connections().getConnectionCredentials(connectionLink);
      const headers = authHeaders(credentials);
      if (!headers.Authorization) return res.status(502).json({ status:'failure', reason:'CONNECTION_RETURNED_NO_AUTHORIZATION', credential_exposure:false });
      const params = credentials && credentials.parameters ? credentials.parameters : {};
      const domain = params.api_domain || params.apiDomain || 'https://www.zohoapis.com';
      const crm = await httpGet(`${String(domain).replace(/\/$/,'')}/crm/v8/Accounts?per_page=1`, headers);
      return res.status(crm.statusCode >= 200 && crm.statusCode < 300 ? 200 : 502).json({
        status: crm.statusCode >= 200 && crm.statusCode < 300 ? 'success' : 'failure',
        operation_code:'CRM_ACCOUNT_READ_TEST',
        crm_http_status:crm.statusCode,
        record_count:Array.isArray(crm.body && crm.body.data) ? crm.body.data.length : null,
        credential_exposure:false
      });
    }

    return res.status(403).json({ status:'rejected', reason:'OPERATION_NOT_IMPLEMENTED_OR_NOT_ALLOWLISTED' });
  } catch (err) {
    res.status(500).json({ status:'failure', reason:'EXECUTION_ERROR', error:safeError(err), credential_exposure:false });
  }
});

app.use((_req, res) => res.status(404).json({ status:'not_found' }));

const port = process.env.X_ZOHO_CATALYST_LISTEN_PORT || 9000;
app.listen(port, () => console.log(`kongoni_mcp_execution_gateway listening on ${port}`));
