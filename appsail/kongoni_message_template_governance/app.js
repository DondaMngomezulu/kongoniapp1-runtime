const express = require('express');
const catalyst = require('zcatalyst-sdk-node');
const {
  TEMPLATE_ID,
  assertToken,
  normalizeImplementation,
  resolveFromRows
} = require('./resolver');

const app = express();
app.use(express.json({ limit: '256kb' }));

const PORT = process.env.X_ZOHO_CATALYST_LISTEN_PORT || 9000;
const REGISTER_TABLE = 'TemplateGovernanceRegister';
const SERVICE_ID = 'SRV-VS00-MSG-TPL-001';
const LOGICAL_REGISTER = 'REG-MSG-TPL-001';

function correlationId(req) {
  const supplied = req.get('x-correlation-id');
  if (supplied && /^[A-Za-z0-9_.:-]{1,120}$/.test(supplied)) return supplied;
  return `${SERVICE_ID}:${Date.now()}:${Math.random().toString(36).slice(2, 10)}`;
}

async function getRegisterRows(req) {
  const catalystApp = catalyst.initialize(req, { scope: 'admin' });
  const table = catalystApp.datastore().table(REGISTER_TABLE);
  const rows = [];
  let nextToken;

  do {
    const result = await table.getPagedRows({ maxRows: 200, nextToken });
    rows.push(...(result.data || []));
    nextToken = result.more_records ? result.next_token : undefined;
  } while (nextToken);

  return rows;
}

function validateResolutionRequest(body) {
  const required = [
    'business_event_id',
    'value_stream_id',
    'cat_msg_template_id',
    'channel_profile',
    'rendering_profile',
    'mandate_id',
    'agent_id'
  ];
  for (const field of required) {
    assertToken(body[field], field, field === 'cat_msg_template_id' ? TEMPLATE_ID : undefined);
  }
  return body;
}

function sendControlError(res, error, cid) {
  const known = ['MESSAGE_TEMPLATE_GAP', 'CONTROL_EXCEPTION', 'INVALID_INPUT'];
  const code = known.includes(error.code) ? error.code : 'INTERNAL_CONTROL_ERROR';
  const status = code === 'MESSAGE_TEMPLATE_GAP' ? 404 : code === 'INVALID_INPUT' ? 400 : code === 'CONTROL_EXCEPTION' ? 409 : 500;
  res.status(status).json({
    status: 'BLOCKED',
    control_result: code,
    message: error.message,
    correlation_id: cid,
    service_id: SERVICE_ID,
    logical_register: LOGICAL_REGISTER
  });
}

app.get('/health', (_req, res) => {
  res.json({
    status: 'ok',
    service_id: SERVICE_ID,
    logical_register: LOGICAL_REGISTER,
    physical_register: REGISTER_TABLE,
    semantic_authority: 'CAT-MSG-001',
    environment: process.env.X_ZOHO_CATALYST_IS_LOCAL === 'true' ? 'local' : 'catalyst'
  });
});

app.get('/v1/message-templates/implementations/:templateId', async (req, res) => {
  const cid = correlationId(req);
  try {
    assertToken(req.params.templateId, 'templateId', TEMPLATE_ID);
    const rows = await getRegisterRows(req);
    const implementations = rows
      .filter((row) => row.EntryType === 'MessageTemplateImplementation' && row.TemplateID === req.params.templateId)
      .map(normalizeImplementation);
    res.json({
      status: 'ok',
      cat_msg_template_id: req.params.templateId,
      implementations,
      correlation_id: cid
    });
  } catch (error) {
    sendControlError(res, error, cid);
  }
});

app.post('/v1/message-templates/resolve', async (req, res) => {
  const cid = correlationId(req);
  try {
    const input = validateResolutionRequest(req.body || {});
    const rows = await getRegisterRows(req);
    const implementation = resolveFromRows(rows, input);

    console.log(JSON.stringify({
      event: 'MESSAGE_TEMPLATE_IMPLEMENTATION_RESOLVED',
      service_id: SERVICE_ID,
      correlation_id: cid,
      agent_id: input.agent_id,
      mandate_id: input.mandate_id,
      business_event_id: input.business_event_id,
      value_stream_id: input.value_stream_id,
      cat_msg_template_id: input.cat_msg_template_id,
      implementation_id: implementation.implementation_id,
      implementation_version: implementation.implementation_version,
      channel_profile: input.channel_profile,
      rendering_profile: input.rendering_profile
    }));

    res.json({
      status: 'RESOLVED',
      correlation_id: cid,
      service_id: SERVICE_ID,
      runtime_next_gate: 'CHANNEL_PROFILE',
      implementation
    });
  } catch (error) {
    sendControlError(res, error, cid);
  }
});

app.use((_req, res) => {
  res.status(404).json({ status: 'BLOCKED', control_result: 'ROUTE_NOT_FOUND', service_id: SERVICE_ID });
});

app.listen(PORT, () => {
  console.log(`${SERVICE_ID} listening on port ${PORT}`);
});

module.exports = app;
