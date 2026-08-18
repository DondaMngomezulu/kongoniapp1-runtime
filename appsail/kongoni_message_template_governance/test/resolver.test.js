const test = require('node:test');
const assert = require('node:assert/strict');
const { resolveFromRows } = require('../resolver');

const baseRequest = {
  business_event_id: 'EVT-001',
  value_stream_id: 'VS00',
  cat_msg_template_id: 'MSG-INF-001',
  channel_profile: 'CHATGPT',
  rendering_profile: 'KONGONI_GOVERNED_MESSAGE_V1',
  mandate_id: 'MANDATE-001',
  agent_id: 'AGENT-001'
};

const activeRow = {
  ROWID: '1',
  EntryID: 'MSGIMPL-CHATGPT-INF-001-V1',
  EntryType: 'MessageTemplateImplementation',
  TemplateID: 'MSG-INF-001',
  TemplateVersion: '1.0',
  Status: 'ACTIVE',
  Authority: 'CTL-COM-MSG-TPL-001',
  OwningValueStreamID: 'VS00',
  ConformanceStatus: 'PASS',
  ConformanceEvidenceRef: 'TEST-001',
  ApplicationScope: JSON.stringify({
    channel_profile: 'CHATGPT',
    rendering_profile: 'KONGONI_GOVERNED_MESSAGE_V1'
  })
};

test('resolves exactly one active implementation', () => {
  const result = resolveFromRows([activeRow], baseRequest);
  assert.equal(result.cat_msg_template_id, 'MSG-INF-001');
  assert.equal(result.implementation_id, 'MSGIMPL-CHATGPT-INF-001-V1');
});

test('fails closed when implementation is absent', () => {
  assert.throws(() => resolveFromRows([], baseRequest), /MESSAGE_TEMPLATE_GAP/);
});

test('fails closed when channel differs', () => {
  assert.throws(
    () => resolveFromRows([activeRow], { ...baseRequest, channel_profile: 'EMAIL' }),
    /MESSAGE_TEMPLATE_GAP/
  );
});

test('excludes superseded implementations', () => {
  assert.throws(
    () => resolveFromRows([{ ...activeRow, Status: 'SUPERSEDED' }], baseRequest),
    /MESSAGE_TEMPLATE_GAP/
  );
});

test('blocks ambiguous active implementations', () => {
  assert.throws(
    () => resolveFromRows([activeRow, { ...activeRow, ROWID: '2', EntryID: 'MSGIMPL-CHATGPT-INF-001-V2' }], baseRequest),
    /AMBIGUOUS_MESSAGE_TEMPLATE_IMPLEMENTATION/
  );
});

test('rejects invalid canonical template identifiers', () => {
  assert.throws(
    () => resolveFromRows([activeRow], { ...baseRequest, cat_msg_template_id: 'TPL-KNG-LETTER-001' }),
    /INVALID_CAT_MSG_TEMPLATE_ID/
  );
});
