#!/usr/bin/env python3
"""Development-only enterprise message schema release decision. No sends."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "outbound-release-evidence.candidate.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())

def evaluate(record, approved_profiles, approved_standards):
    """Fail closed: registries MUST come from independently trusted snapshots, not message claims."""
    errors = sorted(VALIDATOR.iter_errors(record), key=lambda e: tuple(map(str, e.path)))
    if errors:
        return {"decision":"DENY","reasons":["STRUCTURE_INVALID:" + "/".join(map(str,e.path)) for e in errors]}
    reasons = []
    standard = record["standard"]
    profile = record["profile"]
    matching_standard = approved_standards.get(standard["registerId"])
    if not matching_standard or any(matching_standard.get(k) != standard[k] for k in ("family","edition","artifactUri","artifactKind")):
        reasons.append("STANDARD_NOT_VERIFIED")
    if standard["status"] != "APPROVED":
        reasons.append("STANDARD_NOT_APPROVED")
    matching_profile = approved_profiles.get(profile["id"])
    if not matching_profile or any(matching_profile.get(k) != profile[k] for k in ("version","registryEntry")):
        reasons.append("PROFILE_NOT_VERIFIED")
    if profile["approval"] != "APPROVED" or not matching_profile or matching_profile.get("approval") != "APPROVED":
        reasons.append("PROFILE_NOT_APPROVED")
    if not profile["semanticMappingVerified"]:
        reasons.append("SEMANTIC_MAPPING_NOT_VERIFIED")
    if record["payload"]["schemaUri"] != standard["artifactUri"] or record["payload"]["normativeConformance"] != "PASS":
        reasons.append("NORMATIVE_PAYLOAD_NOT_VERIFIED")
    tmpl = record["template"]
    if tmpl["approval"] != "APPROVED" or not tmpl["renderingVerified"] or not tmpl["mergeFieldsResolved"] or tmpl.get("parentDocumentValid") is False:
        reasons.append("TEMPLATE_NOT_RELEASED")
    if not record["parties"]["issuerVerified"] or not record["parties"]["recipientVerified"]:
        reasons.append("PARTY_NOT_VERIFIED")
    channel = record["channel"]
    if not channel["channelVerified"] or not channel["consentVerified"]:
        reasons.append("CHANNEL_OR_CONSENT_INVALID")
    if not record["authority"]["approved"]:
        reasons.append("AUTHORITY_MISSING")
    checks = record["validation"]
    if not checks["schemaPassed"] or not checks["businessRulesPassed"] or not checks["runtimeReceiptVerified"]:
        reasons.append("VALIDATION_EVIDENCE_MISSING")
    delivery = record["delivery"]
    if not delivery["adapterGateVerified"] or not delivery["channelIdMatches"]:
        reasons.append("DELIVERY_PATH_NOT_PROTECTED")
    return {"decision":"DENY" if reasons else "ALLOW_CANDIDATE_ONLY","reasons":sorted(set(reasons))}

if __name__ == "__main__":
    print("Review-only module. Invoke evaluate() with trusted register snapshots and independent runtime evidence. Never use ALLOW_CANDIDATE_ONLY as send authority.")
    sys.exit(0)
