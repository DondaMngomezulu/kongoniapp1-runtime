"""Simulation-only tests: no network, no CRM write, no real delivery."""
import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import sys
import unittest

CTRL = Path(__file__).resolve().parents[1] / "controls"
sys.path.insert(0, str(CTRL))
from exact_instance_review import APPROVAL_SCOPE, digest_instance
from outbox_rehearsal import (
    REQUIRED_PROOFS, SyntheticAuthority, InMemoryReservationLedger,
    InMemoryTransportSink, rehearse
)

NOW = datetime(2026, 10, 20, tzinfo=timezone.utc)
FILE = b"synthetic document, no customer information"


def case(intent="FINANCE_LEASE"):
    parent = "b"*64 if intent == "FINANCE_LEASE" else None
    files = {
        "attachment.pdf": FILE
    }
    instance = {
        "instance_id": "synthetic-issue-1", "crm_record_id": "synthetic-record",
        "intent": intent, "action": "SEND", "channel": "CH-EMAIL",
        "issuer_id": "synthetic-company", "sender_id": "synthetic-agent",
        "adapter_id": "simulated-crm-adapter", "template_id": "synthetic-template",
        "template_version": "1", "template_sha256": "a"*64,
        "parent_instance_sha256": parent, "subject": "Synthetic testing only",
        "body": "Synthetic message (not an offer)", "to": ["recipient@example.test"],
        "cc": [], "bcc": [], "attachments": [
            {"name": "attachment.pdf", "media_type": "application/pdf",
             "sha256": sha256(FILE).hexdigest()}
        ], "idempotency_key": "synthetic-unique-1"
    }
    approval = {k: copy.deepcopy(instance[k]) for k in APPROVAL_SCOPE}
    approval.update({
        "status": "APPROVED",
        "instance_sha256": digest_instance(instance, files),
        "to": list(instance["to"]), "cc": [], "bcc": [],
        "expires_at": "2027-10-20T00:00:00+00:00",
        "receipt_id": "synthetic-receipt", "approver_id": "synthetic-approver"
    })
    proofs = dict.fromkeys(REQUIRED_PROOFS, True)
    proofs.update({"commercial_release_verified": True, "credit_release_verified": True})
    scope = {
        k: copy.deepcopy(instance[k]) for k in (
            "instance_id", "crm_record_id", "issuer_id", "sender_id",
            "adapter_id", "template_id", "template_version", "template_sha256",
            "channel", "intent", "action", "idempotency_key"
        )
    }
    authority = SyntheticAuthority(approval, scope, proofs)
    ledger = InMemoryReservationLedger()
    sink = InMemoryTransportSink()
    return instance, files, authority, ledger, sink


def run(args):
    return rehearse(*args, now=NOW)


class OutboxRehearsalTests(unittest.TestCase):
    def test_nominal_records_simulated_only(self):
        args = case()
        answer = run(args)
        self.assertEqual(answer["decision"], "REHEARSAL_RECORDED_ONLY")
        self.assertFalse(answer["production_release_allowed"])
        self.assertEqual(len(args[-1].events), 1)
        self.assertTrue(args[-1].events[0]["simulation_only"])
        self.assertEqual(args[-2].records["synthetic-unique-1"]["status"], "RECORDED_REHEARSAL")

    def test_duplicate_idempotency_is_blocked(self):
        args = case()
        self.assertEqual(run(args)["decision"], "REHEARSAL_RECORDED_ONLY")
        second = run(args)
        self.assertEqual(second["decision"], "DENY")
        self.assertIn("IDEMPOTENCY_ALREADY_RESERVED", second["reason_codes"])
        self.assertEqual(len(args[-1].events), 1)

    def test_concurrent_idempotency_single_capture(self):
        args = case()
        with ThreadPoolExecutor(max_workers=12) as pool:
            answers = list(pool.map(lambda _: run(args), range(30)))
        self.assertEqual(sum(r["decision"] == "REHEARSAL_RECORDED_ONLY" for r in answers), 1)
        self.assertEqual(len(args[-1].events), 1)
        self.assertTrue(all(not r["production_release_allowed"] for r in answers))

    def test_missing_trust_evidence_denied(self):
        for flag in sorted(REQUIRED_PROOFS):
            with self.subTest(flag=flag):
                args = case()
                args[2].proofs[flag] = False
                answer = run(args)
                self.assertEqual(answer["decision"], "DENY")
                self.assertIn("UNVERIFIED_" + flag.upper(), answer["reason_codes"])
                self.assertEqual(len(args[-1].events), 0)

    def test_credit_hold_denies_finance_offer(self):
        args = case()
        args[2].proofs["credit_release_verified"] = False
        answer = run(args)
        self.assertIn("CREDIT_APPROVAL_HOLD", answer["reason_codes"])
        self.assertEqual(len(args[-1].events), 0)

    def test_commercial_hold_denies_finance_offer(self):
        args = case()
        args[2].proofs["commercial_release_verified"] = False
        answer = run(args)
        self.assertIn("COMMERCIAL_RELEASE_HOLD", answer["reason_codes"])

    def test_underwriting_information_request_not_equivalent_to_offer(self):
        args = case(intent="UNDERWRITING_DOCUMENT_REQUEST")
        args[2].proofs["credit_release_verified"] = False
        args[2].proofs["commercial_release_verified"] = False
        answer = run(args)
        self.assertEqual(answer["decision"], "REHEARSAL_RECORDED_ONLY")
        self.assertFalse(answer["production_release_allowed"])

    def test_unclassified_intent_denied(self):
        args = case(intent="UNCLASSIFIED")
        self.assertIn("INTENT_NOT_CLASSIFIED_FOR_GATE", run(args)["reason_codes"])

    def test_tampered_message_denied(self):
        args = case()
        args[0]["subject"] = "Tampered"
        result = run(args)
        self.assertEqual(result["decision"], "DENY")
        self.assertEqual(len(args[-1].events), 0)

    def test_revocation_before_reservation(self):
        args = case()
        def revoker(authority):
            if authority.read_count == 2:
                authority.approval["status"] = "REVOKED"
        args[2].on_read = revoker
        self.assertIn("AUTHORITY_CHANGED_BEFORE_RESERVATION", run(args)["reason_codes"])
        self.assertEqual(len(args[-1].events), 0)
        self.assertFalse(args[-2].records)

    def test_revocation_after_reservation_quarantines(self):
        args = case()
        def revoker(authority):
            if authority.read_count == 3:
                authority.approval["status"] = "REVOKED"
        args[2].on_read = revoker
        self.assertIn("AUTHORITY_CHANGED_AFTER_RESERVATION", run(args)["reason_codes"])
        self.assertEqual(args[-2].records["synthetic-unique-1"]["status"], "QUARANTINED_REHEARSAL")
        self.assertEqual(len(args[-1].events), 0)

    def test_provider_timeout_unknown_outcome_never_retried(self):
        args = case()
        args[-1].fail_next = True
        first = run(args)
        self.assertEqual(first["decision"], "QUARANTINE_REVIEW_ONLY")
        self.assertIn("TRANSPORT_OUTCOME_UNKNOWN", first["reason_codes"])
        self.assertEqual(args[-2].records["synthetic-unique-1"]["status"], "UNKNOWN_OUTCOME_REHEARSAL")
        self.assertIn("IDEMPOTENCY_ALREADY_RESERVED", run(args)["reason_codes"])

    def test_arbitrary_client_ports_cannot_turn_into_real_gateway(self):
        args = case()
        answer = rehearse(args[0], args[1], object(), args[3], args[4], now=NOW)
        self.assertEqual(answer["decision"], "DENY")
        self.assertIn("SYNTHETIC_PORTS_REQUIRED", answer["reason_codes"])

    def test_expired_approval_denied(self):
        args = case()
        args[2].approval["expires_at"] = "2026-01-01T00:00:00+00:00"
        answer = run(args)
        self.assertEqual(answer["decision"], "DENY")

if __name__ == "__main__":
    unittest.main()
