const express = require('express');

const app = express();
app.use(express.json());

const PORT = process.env.X_ZOHO_CATALYST_LISTEN_PORT || process.env.PORT || 9000;
const SERVICE_ID = 'MS-VS00-TENDER-MGMT-001';
const VERSION = '0.1.0';
const tenders = new Map();

function requireTenderId(req, res, next) {
  const id = req.params.tender_id;
  if (!id || !id.startsWith('TND-')) {
    return res.status(400).json({error: 'INVALID_TENDER_ID'});
  }
  next();
}

function legalCompliancePayload(tender, requirement) {
  return {
    event: 'TenderRequirementsExtracted',
    tender_opportunity_id: tender.tender_opportunity_id,
    tender_reference: tender.tender_reference,
    requirement_id: requirement.requirement_id,
    obligation_type: requirement.obligation_type,
    authority_source: requirement.authority_source,
    evidence_reference: requirement.evidence_reference,
    owning_value_stream: tender.lead_value_stream,
    crm_opportunity_id: tender.crm_opportunity_id || null
  };
}

app.get('/v1/tenders/health', (_req, res) => {
  res.json({service_id: SERVICE_ID, version: VERSION, status: 'DEVELOPMENT_BASELINE', production_authority: false});
});

app.post('/v1/tenders', (req, res) => {
  const body = req.body || {};
  const id = body.tender_opportunity_id;
  if (!id || !id.startsWith('TND-')) return res.status(400).json({error: 'TENDER_OPPORTUNITY_ID_REQUIRED'});
  if (tenders.has(id)) return res.status(409).json({error: 'DUPLICATE_TENDER_OPPORTUNITY'});
  const record = {
    tender_opportunity_id: id,
    tender_reference: body.tender_reference,
    procuring_entity: body.procuring_entity,
    lead_value_stream: body.lead_value_stream,
    participating_value_streams: body.participating_value_streams || [],
    crm_opportunity_id: body.crm_opportunity_id || null,
    state: 'REGISTERED',
    requirements: [],
    legal_compliance_events: [],
    created_at: new Date().toISOString()
  };
  tenders.set(id, record);
  res.status(201).json(record);
});

app.get('/v1/tenders/:tender_id', requireTenderId, (req, res) => {
  const record = tenders.get(req.params.tender_id);
  if (!record) return res.status(404).json({error: 'TENDER_NOT_FOUND'});
  res.json(record);
});

app.post('/v1/tenders/:tender_id/requirements', requireTenderId, (req, res) => {
  const record = tenders.get(req.params.tender_id);
  if (!record) return res.status(404).json({error: 'TENDER_NOT_FOUND'});
  const requirements = Array.isArray(req.body.requirements) ? req.body.requirements : [];
  for (const r of requirements) {
    if (!r.requirement_id || !r.evidence_reference) return res.status(400).json({error: 'REQUIREMENT_EVIDENCE_REQUIRED'});
    record.requirements.push(r);
    if (r.legal_or_compliance_obligation_present === true) {
      if (!r.obligation_type || !r.authority_source) return res.status(400).json({error: 'LEGAL_COMPLIANCE_TRIGGER_FIELDS_REQUIRED'});
      record.legal_compliance_events.push(legalCompliancePayload(record, r));
    }
  }
  record.state = 'REQUIREMENTS_EXTRACTED';
  res.status(200).json({tender_opportunity_id: record.tender_opportunity_id, state: record.state, legal_compliance_events: record.legal_compliance_events});
});

app.post('/v1/tenders/:tender_id/qualification', requireTenderId, (req, res) => {
  const record = tenders.get(req.params.tender_id);
  if (!record) return res.status(404).json({error: 'TENDER_NOT_FOUND'});
  record.qualification = req.body;
  record.state = 'QUALIFICATION';
  res.json({tender_opportunity_id: record.tender_opportunity_id, state: record.state});
});

app.post('/v1/tenders/:tender_id/bid-decision', requireTenderId, (req, res) => {
  const record = tenders.get(req.params.tender_id);
  if (!record) return res.status(404).json({error: 'TENDER_NOT_FOUND'});
  const allowed = ['GO','CONDITIONAL_GO','NO_GO','ESCALATE'];
  if (!allowed.includes(req.body.decision)) return res.status(400).json({error: 'INVALID_BID_DECISION'});
  record.bid_decision = req.body;
  record.state = 'BID_NO_BID';
  res.json({tender_opportunity_id: record.tender_opportunity_id, state: record.state, decision: req.body.decision});
});

app.post('/v1/tenders/:tender_id/compliance-ready', requireTenderId, (req, res) => {
  const record = tenders.get(req.params.tender_id);
  if (!record) return res.status(404).json({error: 'TENDER_NOT_FOUND'});
  const triggered = record.legal_compliance_events.length;
  const assessments = Array.isArray(req.body.assessments) ? req.body.assessments : [];
  const unresolved = assessments.filter(a => ['FAIL','ESCALATE'].includes(a.decision));
  if (assessments.length < triggered || unresolved.length > 0) {
    return res.status(409).json({error: 'LEGAL_COMPLIANCE_GATE_BLOCKED', triggered, assessments: assessments.length, unresolved});
  }
  record.state = 'COMPLIANCE_READY';
  res.json({tender_opportunity_id: record.tender_opportunity_id, state: record.state});
});

app.listen(PORT, () => console.log(`${SERVICE_ID} listening on ${PORT}`));
