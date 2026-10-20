"""Synthetic two-phase outbox rehearsal for AI-NATIVE-ISSUE-SEND-001.

This is NOT a CRM function, provider adapter, authorisation service, sender,
persistent ledger or production egress gate. It can only record a simulated
delivery to an in-memory sink. Positive test results remain REVIEW_ONLY.
"""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from threading import Lock
import json

from exact_instance_review import InvalidInstance, digest_instance, review

FINANCIAL_OFFER_INTENTS = frozenset({
    "FINANCE_LEASE", "OPERATING_LEASE", "QUOTATION", "AGREEMENT"
})
# Underwriting information collection is a separate non-offer purpose:
NON_OFFER_INTENTS = frozenset({"UNDERWRITING_DOCUMENT_REQUEST", "INFORMATION_REQUEST"})
REQUIRED_PROOFS = frozenset({
    "source_fresh", "template_approved", "rendered_document_verified",
    "issuer_authorised", "recipient_authorised", "channel_consent_verified",
    "current_exact_approval_verified", "approval_signature_verified",
    "agent_direct_egress_denied", "exclusive_transport_verified",
    "adapter_credential_isolated", "persistent_ledger_design_verified"
})


def _fingerprint(state):
    """Detect a changed authoritative-state snapshot within a rehearsal."""
    return sha256(json.dumps(state, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


class SyntheticAuthority:
    """Mutable synthetic fixture; NOT a substitute for CRM authenticated readback."""
    def __init__(self, approval, scope, proofs, *, status="ACTIVE", revision="synthetic-r1"):
        self.approval = deepcopy(approval)
        self.scope = deepcopy(scope)
        self.proofs = dict(proofs)
        self.status = status
        self.revision = revision
        self.on_read = None
        self.read_count = 0

    def read_current(self):
        self.read_count += 1
        if self.on_read is not None:
            self.on_read(self)
        return deepcopy({
            "approval": self.approval,
            "scope": self.scope,
            "proofs": self.proofs,
            "status": self.status,
            "revision": self.revision,
        })


class InMemoryReservationLedger:
    """Atomic process-local rehearsal only. No restart durability; NO production use."""
    def __init__(self):
        self._lock = Lock()
        self.records = {}

    def reserve_once(self, key, digest):
        with self._lock:
            if key in self.records:
                return False
            self.records[key] = {"digest": digest, "status": "RESERVED_REHEARSAL"}
            return True

    def finish(self, key, status):
        with self._lock:
            if key not in self.records:
                raise ValueError("RESERVATION_NOT_FOUND")
            self.records[key]["status"] = status


class InMemoryTransportSink:
    """Records *only* a simulated digest and synthetic instance identifier."""
    def __init__(self):
        self._lock = Lock()
        self.events = []
        self.fail_next = False

    def record_simulated(self, *, instance_id, digest, adapter_id):
        with self._lock:
            if self.fail_next:
                self.fail_next = False
                raise RuntimeError("SYNTHETIC_TRANSPORT_TIMEOUT")
            self.events.append({"instance_id": instance_id, "digest": digest,
                                "adapter_id": adapter_id, "simulation_only": True})


def _deny(reason, *, state="DENY"):
    return {"decision": state, "reason_codes": [reason], "production_release_allowed": False}


def _validate_authority(state, instance, now, attachments):
    if not isinstance(state, dict) or state.get("status") != "ACTIVE":
        return _deny("AUTHORITATIVE_STATE_UNAVAILABLE")
    if not state.get("revision"):
        return _deny("SOURCE_REVISION_UNAVAILABLE")
    scope = state.get("scope") or {}
    for field in ("instance_id", "crm_record_id", "issuer_id", "sender_id",
                  "adapter_id", "template_id", "template_version", "template_sha256",
                  "channel", "intent", "action", "idempotency_key"):
        if scope.get(field) != instance.get(field):
            return _deny("TRUSTED_SCOPE_MISMATCH_" + field.upper())
    proofs = state.get("proofs")
    if not isinstance(proofs, dict):
        return _deny("INDEPENDENT_PROOFS_MISSING")
    for field in sorted(REQUIRED_PROOFS):
        if proofs.get(field) is not True:
            return _deny("UNVERIFIED_" + field.upper())
    if instance.get("intent") in FINANCIAL_OFFER_INTENTS:
        if proofs.get("commercial_release_verified") is not True:
            return _deny("COMMERCIAL_RELEASE_HOLD")
        if proofs.get("credit_release_verified") is not True:
            return _deny("CREDIT_APPROVAL_HOLD")
    elif instance.get("intent") not in NON_OFFER_INTENTS:
        return _deny("INTENT_NOT_CLASSIFIED_FOR_GATE")
    p = review(instance, attachments, state.get("approval"), now)
    if p["decision"] != "REVIEW_ONLY":
        return _deny("EXACT_INSTANCE_" + p["reason_codes"][0])
    return None


def rehearse(instance, attachments, authority, ledger, sink, *, now=None):
    """Simulate a guarded send. Does not touch a provider or real CRM record.

    Requires fixed synthetic types; do not plug a live transport into this API.
    The in-memory reservation deliberately never resets on uncertain outcomes.
    A production dispatcher needs CRM-owned durable unique reservations, adapter
    identity isolation, exclusive channel egress and security-approved TOCTOU
    guarantees. None of those are supplied by this rehearsal.
    """
    if (not isinstance(authority, SyntheticAuthority) or
            type(ledger) is not InMemoryReservationLedger or
            type(sink) is not InMemoryTransportSink):
        return _deny("SYNTHETIC_PORTS_REQUIRED")
    clock = now if now is not None else datetime.now(timezone.utc)
    if not isinstance(clock, datetime) or clock.tzinfo is None:
        return _deny("CLOCK_UNVERIFIED")
    try:
        digest = digest_instance(instance, attachments)
        first = authority.read_current()
        failure = _validate_authority(first, instance, clock, attachments)
        if failure is not None:
            return failure
        second = authority.read_current()
        if _fingerprint(second) != _fingerprint(first):
            return _deny("AUTHORITY_CHANGED_BEFORE_RESERVATION")
        key = instance["idempotency_key"]
        if not ledger.reserve_once(key, digest):
            return _deny("IDEMPOTENCY_ALREADY_RESERVED")
        # A fresh read immediately before handoff is essential but a production
        # implementation additionally needs a transaction or enforceable lease.
        third = authority.read_current()
        if _fingerprint(third) != _fingerprint(first):
            ledger.finish(key, "QUARANTINED_REHEARSAL")
            return _deny("AUTHORITY_CHANGED_AFTER_RESERVATION")
        failure = _validate_authority(third, instance, clock, attachments)
        if failure is not None:
            ledger.finish(key, "QUARANTINED_REHEARSAL")
            return failure
        try:
            sink.record_simulated(instance_id=instance["instance_id"],
                                  digest=digest, adapter_id=instance["adapter_id"])
        except Exception:
            ledger.finish(key, "UNKNOWN_OUTCOME_REHEARSAL")
            return _deny("TRANSPORT_OUTCOME_UNKNOWN", state="QUARANTINE_REVIEW_ONLY")
        ledger.finish(key, "RECORDED_REHEARSAL")
        return {"decision": "REHEARSAL_RECORDED_ONLY", "reason_codes": [
            "NO_REAL_TRANSPORT_OR_AUTHORISED_CRM_OUTBOX"],
            "instance_sha256": digest, "production_release_allowed": False}
    except (InvalidInstance, TypeError, ValueError, KeyError):
        return _deny("INSTANCE_INVALID_OR_AUTHORITY_UNAVAILABLE")
    except Exception:
        return _deny("UNEXPECTED_REHEARSAL_FAILURE")
