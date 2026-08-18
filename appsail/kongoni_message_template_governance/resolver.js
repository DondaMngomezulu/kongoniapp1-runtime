const TEMPLATE_ID = /^MSG-[A-Z]{3}-\d{3}$/;
const PROFILE_TOKEN = /^[A-Z0-9_.:-]{1,120}$/;

function assertToken(value, field, pattern = PROFILE_TOKEN) {
  if (typeof value !== 'string' || !pattern.test(value)) {
    const error = new Error(`INVALID_${field.toUpperCase()}`);
    error.code = 'INVALID_INPUT';
    error.field = field;
    throw error;
  }
  return value;
}

function parseApplicationScope(value) {
  if (!value) return {};
  if (typeof value === 'object') return value;
  try {
    return JSON.parse(value);
  } catch (_) {
    return { legacy_scope: String(value) };
  }
}

function normalizeImplementation(row) {
  const scope = parseApplicationScope(row.ApplicationScope);
  return {
    cat_msg_template_id: row.TemplateID,
    implementation_id: row.EntryID,
    implementation_version: row.TemplateVersion,
    implementation_status: row.Status,
    channel_profile: scope.channel_profile || null,
    rendering_profile: scope.rendering_profile || null,
    authority: row.Authority,
    conformance_status: row.ConformanceStatus || null,
    conformance_evidence_ref: row.ConformanceEvidenceRef || null,
    owning_value_stream_id: row.OwningValueStreamID || null,
    effective_date: row.EffectiveDate || null,
    provenance: {
      logical_register: 'REG-MSG-TPL-001',
      physical_register: 'TemplateGovernanceRegister',
      catalyst_row_id: row.ROWID || null,
      canonical_source: 'CAT-MSG-001'
    }
  };
}

function matchImplementation(row, request) {
  if (row.EntryType !== 'MessageTemplateImplementation') return false;
  if (row.TemplateID !== request.cat_msg_template_id) return false;
  if (row.Status !== 'ACTIVE' && row.Status !== 'RELEASED') return false;

  const scope = parseApplicationScope(row.ApplicationScope);
  return scope.channel_profile === request.channel_profile &&
    scope.rendering_profile === request.rendering_profile;
}

function resolveFromRows(rows, request) {
  assertToken(request.cat_msg_template_id, 'cat_msg_template_id', TEMPLATE_ID);
  assertToken(request.channel_profile, 'channel_profile');
  assertToken(request.rendering_profile, 'rendering_profile');

  const candidates = rows.filter((row) => matchImplementation(row, request));
  if (candidates.length === 0) {
    const error = new Error('MESSAGE_TEMPLATE_GAP');
    error.code = 'MESSAGE_TEMPLATE_GAP';
    throw error;
  }
  if (candidates.length > 1) {
    const error = new Error('AMBIGUOUS_MESSAGE_TEMPLATE_IMPLEMENTATION');
    error.code = 'CONTROL_EXCEPTION';
    throw error;
  }
  return normalizeImplementation(candidates[0]);
}

module.exports = {
  TEMPLATE_ID,
  assertToken,
  normalizeImplementation,
  parseApplicationScope,
  matchImplementation,
  resolveFromRows
};
