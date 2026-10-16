#!/usr/bin/env python3
"""Synthetic evidence-resolver regression; no live providers or customer data."""
import copy
from datetime import datetime,timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from jsonschema import Draft202012Validator
BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("policy",BASE/"outbound_release_gate.py")
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
NOW=datetime(2026,10,15,18,30,tzinfo=timezone.utc)
PAYLOAD=b'{"messageId":"test","body":"synthetic"}'
DIGEST="sha256:"+sha256(PAYLOAD).hexdigest()
URI="https://example.invalid/synthetic-message-schema.json"
SCHEMA={"type":"object","required":["messageId","body"],"properties":{"messageId":{"type":"string"},"body":{"type":"string"}}}
GOOD={
"messageId":"test","messageType":"Reminder","direction":"OUTBOUND",
"standard":{"family":"OASIS","registerId":"std-1","edition":"fixture","artifactUri":URI,"artifactKind":"JSON_SCHEMA","status":"APPROVED"},
"profile":{"id":"profile-1","version":"1","registryEntry":"test-register","approval":"APPROVED","semanticMappingVerified":True},
"payload":{"schemaUri":URI,"sourceRecordRef":"source-1","payloadDigest":DIGEST,"normativeConformance":"PASS"},
"template":{"id":"tmpl-1","version":"1","approval":"APPROVED","renderingVerified":True,"mergeFieldsResolved":True,"parentDocumentValid":True},
"parties":{"issuerId":"issuer-1","issuerVerified":True,"recipientId":"recipient-1","recipientVerified":True},
"channel":{"id":"email-1","renderingId":"render-1","adapterId":"adapter-1","channelVerified":True,"consentVerified":True},
"authority":{"actorId":"actor-1","approved":True,"approvalEvidenceRef":"approval-1"},
"validation":{"schemaPassed":True,"businessRulesPassed":True,"evidenceRef":"validation-1","engineVersion":"fixture","runtimeReceiptVerified":True},
"delivery":{"correlationId":"corr-1","idempotencyKey":"reservation-1","auditRef":"audit-1","adapterGateVerified":True,"channelIdMatches":True}}
def row(**kwargs):
 return dict(status="APPROVED",revoked=False,validUntil="2027-01-01T00:00:00Z",**kwargs)
class Resolver(p.EvidenceResolver):
 def __init__(self):
  self.artifact_ok=True
  self.data={
   "standard":{"std-1":row(family="OASIS",edition="fixture",artifactUri=URI,artifactKind="JSON_SCHEMA")},
   "profile":{"profile-1":row(version="1",registryEntry="test-register",standardId="std-1")},
   "message_type":{"Reminder":row(standardId="std-1",profileId="profile-1",templateId="tmpl-1",channelId="email-1")},
   "template":{"tmpl-1:1":row(id="tmpl-1",version="1",messageType="Reminder",profileId="profile-1",channelId="email-1")},
   "issuer":{"issuer-1":row(status="ACTIVE",verified=True)},
   "recipient":{"recipient-1":row(status="ACTIVE",verified=True)},
   "source":{"source-1":row(status="ACTIVE",issuerId="issuer-1",recipientId="recipient-1",messageType="Reminder")},
   "channel":{"email-1":row()},
   "rendering":{"render-1":row(channelId="email-1",templateId="tmpl-1")},
   "adapter":{"adapter-1":row(channelId="email-1",egressGateRequired=True)},
   "consent":{"recipient-1:email-1":row(status="GRANTED")},
   "approval":{"approval-1":row(messageId="test",actorId="actor-1",messageType="Reminder",issuerId="issuer-1",recipientId="recipient-1",templateId="tmpl-1",templateVersion="1",channelId="email-1",payloadDigest=DIGEST)},
   "validation":{"validation-1":row(status="PASS",messageId="test",payloadDigest=DIGEST,standardId="std-1",artifactUri=URI,profileId="profile-1",profileVersion="1",engineVersion="fixture",normativePassed=True,businessRulesPassed=True)},
   "audit":{"audit-1":row(status="PREPARED",messageId="test",payloadDigest=DIGEST,approvalRef="approval-1",validationRef="validation-1",correlationId="corr-1",idempotencyKey="reservation-1",channelId="email-1",appendOnly=True)},
   "dispatch":{"reservation-1":row(status="RESERVED",messageId="test",payloadDigest=DIGEST,adapterId="adapter-1",auditRef="audit-1",channelId="email-1",egressGateEnforced=True)}}
 def lookup(self,kind,key): return copy.deepcopy(self.data.get(kind,{}).get(key))
 def validate_payload(self,standard,payload):
  return self.artifact_ok and standard["artifactUri"]==URI and Draft202012Validator(SCHEMA).is_valid(json.loads(payload))
def result(r=GOOD,s=None,payload=PAYLOAD):
 return p.evaluate(r,payload=payload,resolver=Resolver() if s is None else s,now=NOW)
def deny(r=GOOD,s=None,payload=PAYLOAD):
 out=result(r,s,payload);assert out["decision"]=="DENY",out
assert result()["decision"]=="ALLOW_CANDIDATE_ONLY"
attacks=[("template","id","other"),(None,"messageType","InsuranceClaim"),("authority","approvalEvidenceRef","fake"),("validation","evidenceRef","fake"),("channel","renderingId","fake"),("channel","adapterId","fake"),("parties","issuerId","fake"),("payload","payloadDigest","sha256:"+"b"*64),("delivery","auditRef","fake")]
for section,key,value in attacks:
 r=copy.deepcopy(GOOD);(r if section is None else r[section])[key]=value;deny(r)
legacy=[("standard","status","HOLD"),("standard","edition","older"),("profile","approval","HOLD"),("profile","semanticMappingVerified",False),("profile","id","missing"),("payload","normativeConformance","NOT_TESTED"),("payload","schemaUri","https://example.invalid/other"),("template","approval","HOLD"),("template","renderingVerified",False),("template","mergeFieldsResolved",False),("template","parentDocumentValid",False),("parties","issuerVerified",False),("parties","recipientVerified",False),("channel","channelVerified",False),("channel","consentVerified",False),("authority","approved",False),("validation","schemaPassed",False),("validation","businessRulesPassed",False),("validation","runtimeReceiptVerified",False),("delivery","adapterGateVerified",False),("delivery","channelIdMatches",False)]
for section,key,value in legacy:
 r=copy.deepcopy(GOOD);r[section][key]=value;deny(r)
for field in GOOD:
 r=copy.deepcopy(GOOD);r.pop(field);deny(r)
for typ,key,field,value in [("template","tmpl-1:1","channelId","other"),("message_type","Reminder","standardId","other"),("approval","approval-1","payloadDigest","different"),("validation","validation-1","normativePassed",False),("audit","audit-1","appendOnly",False),("dispatch","reservation-1","status","CONSUMED"),("issuer","issuer-1","verified",False),("recipient","recipient-1","verified",False),("adapter","adapter-1","egressGateRequired",False),("consent","recipient-1:email-1","status","REVOKED")]:
 s=Resolver();s.data[typ][key][field]=value;deny(s=s)
s=Resolver();s.artifact_ok=False;deny(s=s)
s=Resolver();s.data["approval"]["approval-1"]["validUntil"]="2026-10-14T00:00:00Z";deny(s=s)
deny(s=object())
deny(payload=b'{"messageId":"changed","body":"different"}')
print("PASS: 1 synthetic positive; 9 prior bypasses denied; 21 legacy cases; 12 top-level fields; 10 trusted evidence tampering; expiry, validator outage, missing resolver and payload alteration.")
