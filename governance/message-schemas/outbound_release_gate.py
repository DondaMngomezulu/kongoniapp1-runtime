#!/usr/bin/env python3
"""Review-only outbound policy. Never dispatch from this module.

Security boundary: EvidenceResolver MUST be implemented by a trusted server-side
adapter with authenticated read access to the governed registers and append-only
receipts. Request data/AI assertions must never populate this resolver.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "outbound-release-evidence.candidate.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


class EvidenceResolver(ABC):
    """Trusted, authenticated, read-only authority port; NOT a message field.

    The real implementation must verify source identities, snapshot provenance,
    signatures/authorization, revocation, freshness, and immutable receipts.
    Arbitrary dictionaries supplied by message authors do not meet this contract.
    """

    @abstractmethod
    def lookup(self, category: str, key: str) -> dict | None:
        """Fetch current verified evidence from the *authoritative* system."""

    @abstractmethod
    def validate_payload(self, standard: dict, payload: bytes) -> bool:
        """Validate real payload against pinned, trusted normative artifact.

        Must use local pinned XSD dependencies/OpenAPI/JSON Schema as appropriate;
        never fetch or execute a URL contained in an untrusted message.
        """


def _current(item, statuses, now):
    if not isinstance(item, dict) or item.get("status") not in statuses:
        return False
    if item.get("revoked") is True:
        return False
    try:
        start, end = item.get("effectiveFrom"), item.get("validUntil")
        parse = lambda value: datetime.fromisoformat(value.replace("Z", "+00:00"))
        if start and parse(start) > now:
            return False
        if end and parse(end) <= now:
            return False
    except (TypeError, ValueError):
        return False
    return True


def _fields_equal(entry, values):
    return isinstance(entry, dict) and all(entry.get(k) == v for k, v in values.items())


def evaluate(record, *, payload, resolver, now=None):
    """Deny by default. ALLOW_CANDIDATE_ONLY is never an egress token.

    Never use this as a production intercept or a permission to send until
    every real provider egress path is bound to an approved runtime controller.
    """
    if not isinstance(record, dict):
        return {"decision": "DENY", "reasons": ["STRUCTURE_INVALID"]}
    errors = sorted(VALIDATOR.iter_errors(record), key=lambda e: tuple(map(str, e.path)))
    if errors:
        return {"decision": "DENY", "reasons": ["STRUCTURE_INVALID:" + "/".join(map(str, e.path)) for e in errors]}
    if not isinstance(payload, bytes) or not payload:
        return {"decision": "DENY", "reasons": ["PAYLOAD_UNAVAILABLE"]}
    if not isinstance(resolver, EvidenceResolver):
        return {"decision": "DENY", "reasons": ["TRUSTED_RESOLVER_UNAVAILABLE"]}
    if now is None:
        now = datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None:
        return {"decision": "DENY", "reasons": ["INVALID_CLOCK"]}

    reasons = []
    def check(ok, code):
        if not ok:
            reasons.append(code)

    def lookup(kind, key):
        # The actual runtime adapter MUST authenticate responses; our tests
        # use a dedicated in-memory adapter and never claim production trust.
        entry = resolver.lookup(kind, key)
        if not isinstance(entry, dict):
            return None
        return entry

    try:
        standard, profile = record["standard"], record["profile"]
        body, tmpl, parties = record["payload"], record["template"], record["parties"]
        channel, auth, val, delivery = record["channel"], record["authority"], record["validation"], record["delivery"]
        digest = "sha256:" + sha256(payload).hexdigest()
        check(body["payloadDigest"] == digest, "PAYLOAD_DIGEST_MISMATCH")

        trusted_std = lookup("standard", standard["registerId"])
        std_values = {"family": standard["family"], "edition": standard["edition"], "artifactUri": standard["artifactUri"], "artifactKind": standard["artifactKind"]}
        check(_current(trusted_std, {"APPROVED"}, now) and standard["status"] == "APPROVED" and _fields_equal(trusted_std, std_values), "STANDARD_NOT_VERIFIED")

        trusted_profile = lookup("profile", profile["id"])
        profile_values = {"version": profile["version"], "registryEntry": profile["registryEntry"], "standardId": standard["registerId"]}
        check(_current(trusted_profile, {"APPROVED"}, now) and profile["approval"] == "APPROVED" and _fields_equal(trusted_profile, profile_values) and profile["semanticMappingVerified"] is True, "PROFILE_NOT_VERIFIED")

        # A single approved, joint binding prevents a valid schema from being
        # used for an unrelated message type, profile, template or channel.
        message_type = lookup("message_type", record["messageType"])
        joint = {"standardId": standard["registerId"], "profileId": profile["id"], "templateId": tmpl["id"], "channelId": channel["id"]}
        check(_current(message_type, {"APPROVED"}, now) and _fields_equal(message_type, joint), "MESSAGE_TYPE_BINDING_INVALID")

        trusted_tmpl = lookup("template", tmpl["id"] + ":" + tmpl["version"])
        template_scope = {"id": tmpl["id"], "version": tmpl["version"], "messageType": record["messageType"], "profileId": profile["id"], "channelId": channel["id"]}
        check(_current(trusted_tmpl, {"APPROVED"}, now) and _fields_equal(trusted_tmpl, template_scope) and tmpl["approval"] == "APPROVED" and tmpl["renderingVerified"] is True and tmpl["mergeFieldsResolved"] is True and tmpl.get("parentDocumentValid") is True, "TEMPLATE_NOT_VERIFIED")

        trusted_issuer = lookup("issuer", parties["issuerId"])
        trusted_recipient = lookup("recipient", parties["recipientId"])
        trusted_source = lookup("source", body["sourceRecordRef"])
        check(_current(trusted_issuer, {"ACTIVE"}, now) and trusted_issuer.get("verified") is True and parties["issuerVerified"] is True, "ISSUER_NOT_VERIFIED")
        check(_current(trusted_recipient, {"ACTIVE"}, now) and trusted_recipient.get("verified") is True and parties["recipientVerified"] is True, "RECIPIENT_NOT_VERIFIED")
        check(_current(trusted_source, {"ACTIVE"}, now) and _fields_equal(trusted_source, {"issuerId": parties["issuerId"], "recipientId": parties["recipientId"], "messageType": record["messageType"]}), "SOURCE_BINDING_INVALID")

        trusted_channel = lookup("channel", channel["id"])
        trusted_rendering = lookup("rendering", channel["renderingId"])
        trusted_adapter = lookup("adapter", channel["adapterId"])
        check(_current(trusted_channel, {"APPROVED"}, now) and channel["channelVerified"] is True, "CHANNEL_NOT_VERIFIED")
        check(_current(trusted_rendering, {"APPROVED"}, now) and _fields_equal(trusted_rendering, {"channelId": channel["id"], "templateId": tmpl["id"]}), "RENDERING_NOT_VERIFIED")
        check(_current(trusted_adapter, {"APPROVED"}, now) and _fields_equal(trusted_adapter, {"channelId": channel["id"], "egressGateRequired": True}), "ADAPTER_NOT_VERIFIED")
        consent = lookup("consent", parties["recipientId"] + ":" + channel["id"])
        check(_current(consent, {"GRANTED"}, now) and channel["consentVerified"] is True, "CONSENT_NOT_VERIFIED")

        approval = lookup("approval", auth["approvalEvidenceRef"])
        approval_scope = {"messageId": record["messageId"], "actorId": auth["actorId"], "messageType": record["messageType"], "issuerId": parties["issuerId"], "recipientId": parties["recipientId"], "templateId": tmpl["id"], "templateVersion": tmpl["version"], "channelId": channel["id"], "payloadDigest": digest}
        check(_current(approval, {"APPROVED"}, now) and _fields_equal(approval, approval_scope) and auth["approved"] is True, "APPROVAL_NOT_VERIFIED")

        receipt = lookup("validation", val["evidenceRef"])
        validation_scope = {"messageId": record["messageId"], "payloadDigest": digest, "standardId": standard["registerId"], "artifactUri": standard["artifactUri"], "profileId": profile["id"], "profileVersion": profile["version"], "engineVersion": val["engineVersion"]}
        check(_current(receipt, {"PASS"}, now) and _fields_equal(receipt, validation_scope) and receipt.get("normativePassed") is True and receipt.get("businessRulesPassed") is True and val["schemaPassed"] is True and val["businessRulesPassed"] is True and val["runtimeReceiptVerified"] is True and body["schemaUri"] == standard["artifactUri"] and body["normativeConformance"] == "PASS", "VALIDATION_RECEIPT_INVALID")
        # A report saying PASS is not itself an XSD/JSON Schema validation.
        check(trusted_std is not None and resolver.validate_payload(trusted_std, payload) is True, "NORMATIVE_PAYLOAD_INVALID")

        audit = lookup("audit", delivery["auditRef"])
        audit_scope = {"messageId": record["messageId"], "payloadDigest": digest, "approvalRef": auth["approvalEvidenceRef"], "validationRef": val["evidenceRef"], "correlationId": delivery["correlationId"], "idempotencyKey": delivery["idempotencyKey"], "channelId": channel["id"]}
        check(_current(audit, {"PREPARED"}, now) and _fields_equal(audit, audit_scope) and audit.get("appendOnly") is True, "AUDIT_NOT_VERIFIED")

        dispatch = lookup("dispatch", delivery["idempotencyKey"])
        dispatch_scope = {"messageId": record["messageId"], "payloadDigest": digest, "adapterId": channel["adapterId"], "auditRef": delivery["auditRef"], "channelId": channel["id"]}
        check(_current(dispatch, {"RESERVED"}, now) and _fields_equal(dispatch, dispatch_scope) and dispatch.get("egressGateEnforced") is True and delivery["adapterGateVerified"] is True and delivery["channelIdMatches"] is True, "DISPATCH_NOT_VERIFIED")
    except Exception:
        # Resolver timeout/corrupt authoritative record or any unexpected error
        # must not turn into an affirmative send decision.
        return {"decision": "DENY", "reasons": ["AUTHORITY_OR_VALIDATOR_UNAVAILABLE"]}

    reasons = sorted(set(reasons))
    return {"decision": "DENY" if reasons else "ALLOW_CANDIDATE_ONLY", "reasons": reasons}


if __name__ == "__main__":
    print("Candidate only: no configured trusted resolver, provider integration or permission to send.")
