#!/usr/bin/env python3
"""Synthetic fixtures only; never connected to live channels."""
import copy
import importlib.util
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("policy", BASE / "outbound_release_gate.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
URI = "https://docs.oasis-open.org/ubl/os-UBL-2.5/xsd/maindoc/UBL-Reminder-2.5.xsd"
STANDARDS = {"STD-BDOC-001":{"family":"OASIS","edition":"UBL 2.5","artifactUri":URI,"artifactKind":"XSD"}}
PROFILES = {"EXAMPLE-CANDIDATE":{"version":"0.1","registryEntry":"ROR-0095","approval":"APPROVED"}}
GOOD = {
 "messageId":"synthetic-001","messageType":"PaymentReminder","direction":"OUTBOUND",
 "standard":{"family":"OASIS","registerId":"STD-BDOC-001","edition":"UBL 2.5","artifactUri":URI,"artifactKind":"XSD","status":"APPROVED"},
 "profile":{"id":"EXAMPLE-CANDIDATE","version":"0.1","registryEntry":"ROR-0095","approval":"APPROVED","semanticMappingVerified":True},
 "payload":{"schemaUri":URI,"sourceRecordRef":"synthetic-record","payloadDigest":"sha256:"+"a"*64,"normativeConformance":"PASS"},
 "template":{"id":"synthetic-template","version":"0.1","approval":"APPROVED","renderingVerified":True,"mergeFieldsResolved":True,"parentDocumentValid":True},
 "parties":{"issuerId":"synthetic-org","issuerVerified":True,"recipientId":"synthetic-person","recipientVerified":True},
 "channel":{"id":"synthetic-channel","renderingId":"synthetic-render","adapterId":"synthetic-adapter","channelVerified":True,"consentVerified":True},
 "authority":{"actorId":"synthetic-actor","approved":True,"approvalEvidenceRef":"synthetic-approval"},
 "validation":{"schemaPassed":True,"businessRulesPassed":True,"evidenceRef":"synthetic-test","engineVersion":"fixture-only","runtimeReceiptVerified":True},
 "delivery":{"correlationId":"corr-1","idempotencyKey":"idem-1","auditRef":"synthetic-audit","adapterGateVerified":True,"channelIdMatches":True}
}
assert mod.evaluate(GOOD, PROFILES, STANDARDS)["decision"] == "ALLOW_CANDIDATE_ONLY"
cases = [
 ("standard","status","HOLD"),("standard","edition","UBL 2.4"),("standard","artifactUri","https://example.invalid/bad.xsd"),
 ("profile","approval","HOLD"),("profile","semanticMappingVerified",False),("profile","id","unregistered"),
 ("payload","normativeConformance","NOT_TESTED"),("payload","schemaUri","https://example.invalid/bad.xsd"),
 ("template","approval","DRAFT"),("template","renderingVerified",False),("template","mergeFieldsResolved",False),("template","parentDocumentValid",False),
 ("parties","issuerVerified",False),("parties","recipientVerified",False),
 ("channel","channelVerified",False),("channel","consentVerified",False),
 ("authority","approved",False),("validation","schemaPassed",False),("validation","businessRulesPassed",False),
 ("validation","runtimeReceiptVerified",False),("delivery","adapterGateVerified",False),("delivery","channelIdMatches",False)
]
for block, key, value in cases:
    bad=copy.deepcopy(GOOD)
    bad[block][key]=value
    outcome=mod.evaluate(bad,PROFILES,STANDARDS)
    assert outcome["decision"]=="DENY", (block,key,outcome)
for key in GOOD:
    bad=copy.deepcopy(GOOD)
    bad.pop(key)
    assert mod.evaluate(bad,PROFILES,STANDARDS)["decision"]=="DENY", key
assert mod.evaluate(GOOD, {}, STANDARDS)["decision"]=="DENY"
assert mod.evaluate(GOOD, PROFILES, {})["decision"]=="DENY"
print(f"PASS: 1 synthetic candidate, {len(cases)} negative semantic cases, {len(GOOD)} required-field negatives, 2 missing trusted register cases.")
