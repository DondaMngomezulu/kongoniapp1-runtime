"""Synthetic exact-instance verifier for the governed CRM send-gate twin.

This verifier does not authenticate approvals, own a provider, persist replay locks,
or dispatch. Nominal decisions are REVIEW_ONLY, never an egress capability.
Use with *synthetic* test data; customer data must remain in CRM.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
import re

HEX = re.compile(r"^[a-f0-9]{64}$")
INSTANCE_KEYS = frozenset({
    "instance_id", "crm_record_id", "intent", "action", "channel",
    "issuer_id", "sender_id", "adapter_id", "template_id",
    "template_version", "template_sha256", "parent_instance_sha256",
    "subject", "body", "to", "cc", "bcc", "attachments",
    "idempotency_key"
})
APPROVAL_SCOPE = (
    "instance_id", "crm_record_id", "intent", "action", "channel",
    "issuer_id", "sender_id", "adapter_id", "template_id",
    "template_version", "template_sha256", "parent_instance_sha256",
    "idempotency_key"
)
DOCUMENT_INTENTS = {
    "FINANCE_LEASE", "OPERATING_LEASE", "QUOTATION", "AGREEMENT",
    "INVOICE", "ORDER", "LEGAL_NOTICE", "DELIVERY_NOTE"
}


class InvalidInstance(ValueError):
    """Deny this candidate instance; never authorize transmission."""


def _filled(value):
    return isinstance(value, str) and bool(value.strip())


def _hash(value):
    return isinstance(value, str) and bool(HEX.fullmatch(value))


def _instant(value):
    if not isinstance(value, str):
        raise InvalidInstance("EXPIRY_INVALID")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InvalidInstance("EXPIRY_INVALID") from exc
    if parsed.tzinfo is None:
        raise InvalidInstance("EXPIRY_UNZONED")
    return parsed


def digest_instance(instance, attachment_content):
    """Hash exact UTF-8 instance fields and independently checked attachment bytes.

    Callers must use these precise wire-stage fields, not a separately edited
    message. Provider-level MIME / file transformation still needs adapter QA.
    """
    if not isinstance(instance, dict) or set(instance) != INSTANCE_KEYS:
        raise InvalidInstance("INSTANCE_STRUCTURE_INVALID")
    for k in INSTANCE_KEYS - {"parent_instance_sha256", "attachments", "to", "cc", "bcc"}:
        if not _filled(instance[k]):
            raise InvalidInstance("INSTANCE_FIELD_MISSING_" + k.upper())
    if not _hash(instance["template_sha256"]):
        raise InvalidInstance("TEMPLATE_DIGEST_INVALID")
    if instance["parent_instance_sha256"] is not None and not _hash(instance["parent_instance_sha256"]):
        raise InvalidInstance("PARENT_DIGEST_INVALID")
    if instance["intent"] in DOCUMENT_INTENTS and not instance["parent_instance_sha256"]:
        raise InvalidInstance("PARENT_INSTANCE_REQUIRED")
    addressees = []
    for key in ("to", "cc", "bcc"):
        seq = instance[key]
        if not isinstance(seq, list) or any(not _filled(s) for s in seq):
            raise InvalidInstance("RECIPIENT_STRUCTURE_INVALID")
        addressees.extend(s.casefold() for s in seq)
    if not instance["to"] or len(set(addressees)) != len(addressees):
        raise InvalidInstance("RECIPIENTS_INVALID_OR_DUPLICATE")
    entries = instance["attachments"]
    if not isinstance(entries, list) or not isinstance(attachment_content, dict):
        raise InvalidInstance("ATTACHMENTS_INVALID")
    known = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"name", "media_type", "sha256"}:
            raise InvalidInstance("ATTACHMENT_MANIFEST_INVALID")
        if not _filled(entry["name"]) or not _filled(entry["media_type"]) or not _hash(entry["sha256"]):
            raise InvalidInstance("ATTACHMENT_METADATA_INVALID")
        name = entry["name"]
        if name in known:
            raise InvalidInstance("ATTACHMENT_NAME_DUPLICATE")
        known.add(name)
        binary = attachment_content.get(name)
        if not isinstance(binary, bytes) or sha256(binary).hexdigest() != entry["sha256"]:
            raise InvalidInstance("ATTACHMENT_BYTES_CHANGED")
    if known != set(attachment_content):
        raise InvalidInstance("ATTACHMENT_SET_CHANGED")
    # Strict JSON encoding provides deterministic bytes; do not trim, normalize,
    # or substitute subject/body or audience after approval.
    wire = json.dumps(
        {"profile": "AI-NATIVE-ISSUE-SEND-001/exact-instance-review-v1",
         "instance": instance},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return sha256(wire).hexdigest()


def review(instance, attachment_content, approval, now=None):
    """Evaluate exact scope; returning REVIEW_ONLY never authorizes sending."""
    try:
        digest = digest_instance(instance, attachment_content)
        if not isinstance(approval, dict) or approval.get("status") != "APPROVED":
            raise InvalidInstance("APPROVAL_NOT_ACTIVE")
        if approval.get("instance_sha256") != digest:
            raise InvalidInstance("APPROVED_INSTANCE_CHANGED")
        for key in APPROVAL_SCOPE:
            if key not in approval or approval[key] != instance[key]:
                raise InvalidInstance("APPROVAL_SCOPE_CHANGED_" + key.upper())
        for key in ("to", "cc", "bcc"):
            if approval.get(key) != instance[key]:
                raise InvalidInstance("APPROVED_AUDIENCE_CHANGED_" + key.upper())
        clock = now or datetime.now(timezone.utc)
        if not isinstance(clock, datetime) or clock.tzinfo is None:
            raise InvalidInstance("CLOCK_UNVERIFIED")
        if _instant(approval.get("expires_at")) <= clock:
            raise InvalidInstance("APPROVAL_EXPIRED")
        if not _filled(approval.get("receipt_id")) or not _filled(approval.get("approver_id")):
            raise InvalidInstance("APPROVAL_RECEIPT_MISSING")
    except (InvalidInstance, TypeError, ValueError) as error:
        reason = str(error) if isinstance(error, InvalidInstance) else "INSTANCE_VALIDATION_ERROR"
        return {"decision": "DENY", "reason_codes": [reason], "production_release_allowed": False}
    return {
        "decision": "REVIEW_ONLY",
        "reason_codes": ["TRUSTED_CRM_APPROVAL_AND_EXCLUSIVE_TRANSPORT_NOT_IMPLEMENTED"],
        "instance_sha256": digest,
        "production_release_allowed": False
    }
