"""Negative-path and nominal preflight checks (not a deployed send control)."""
import importlib.util
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "controls" / "release_gate_preflight.py"
spec = importlib.util.spec_from_file_location("preflight", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
H = "a" * 64
T = "b" * 64
good = {
    "intent": "FINANCE_LEASE", "channel": "CH-EMAIL",
    "crm": {"module": "Quotes", "record_id": "q1", "account_id": "a1"},
    "issuer": {"entity_id": "entity-a", "sender_id": "u1"},
    "template": {"id": "msg1", "version": "1", "hash": T, "class": "QUOTE_EMAIL",
                 "status": "CONTROLLED", "approval_receipt": "apr1",
                 "issuer_id": "entity-a", "channels": ["CH-EMAIL"]},
    "parent": {"id": "doc1", "version": "1", "hash": T, "class": "FINANCE_LEASE",
               "status": "CONTROLLED", "approval_receipt": "apr2",
               "issuer_id": "entity-a", "channels": ["CH-EMAIL"]},
    "snapshot": {"source_hash": H, "artifact_hash": T, "merge_status": "PASS"},
    "approval": {"receipt": "receipt1", "approver": "officer1", "status": "APPROVED",
                 "source_hash": H, "artifact_hash": T,
                 "expires_at": "2027-12-31T00:00:00+00:00"},
    "recipients": ["customer@example.test"],
    "transport": {"adapter_id": "crm-gateway", "idempotency_key": "id-1"}
}
proof = dict.fromkeys([
    "independently_authenticated", "recipient_authorised", "sender_authorised",
    "source_hash_verified", "template_hash_verified", "parent_hash_verified",
    "availability_verified", "credit_approval_verified", "pricing_verified",
    "crm_record_current", "channel_access_control_verified",
    "idempotency_key_available", "current_exact_approval_verified"
], True)

def test(label, data, evidence, expected):
    result = m.assess_candidate(data, evidence)
    assert result["decision"] == expected, (label, result)
    return result

assert test("happy", good, proof, "REVIEW_ONLY")["decision"] != "ALLOW"
assert "TRUSTED_EVIDENCE_MISSING" in test("self assertion", good, {}, "DENY")["reason_codes"]
for k, value, expected in [
    ("template", {**good["template"], "status": "HOLD"}, "TEMPLATE_NOT_CONTROLLED"),
    ("channel", "CH-WHATSAPP", "CHANNEL_MISMATCH"),
    ("parent", None, "PARENT_REQUIRED"),
    ("snapshot", {**good["snapshot"], "merge_status": "FAIL"}, "MERGE_INCOMPLETE"),
    ("snapshot", {**good["snapshot"], "source_hash": "c"*64}, "SOURCE_CHANGED"),
    ("approval", {**good["approval"], "status": "PENDING"}, "RELEASE_NOT_APPROVED"),
    ("recipients", [], "RECIPIENT_MISSING"),
]:
    r = test(k, {**good, k: value}, proof, "DENY")
    assert expected in r["reason_codes"], (k, r)

for k, expected in [
    ("credit_approval_verified", "CREDIT_UNVERIFIED"),
    ("availability_verified", "AVAILABILITY_UNVERIFIED"),
    ("pricing_verified", "PRICE_UNVERIFIED"),
    ("channel_access_control_verified", "TRANSPORT_BYPASS_NOT_CLOSED"),
    ("current_exact_approval_verified", "LIVE_APPROVAL_UNVERIFIED"),
    ("idempotency_key_available", "DUPLICATE_OR_UNVERIFIED_SEND"),
]:
    r = test(k, good, {**proof, k: False}, "DENY")
    assert expected in r["reason_codes"]
r = test("account hold", good, {**proof, "account_quote_blocked": True}, "DENY")
assert "ACCOUNT_QUOTE_HOLD" in r["reason_codes"]
print("PASS: 16 representative preflight checks; nominal remains REVIEW_ONLY.")
