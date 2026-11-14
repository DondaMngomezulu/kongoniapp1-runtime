"""Synthetic tamper/replay assertions for the exact-instance review kernel."""
import copy
import importlib.util
import unittest
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

src = Path(__file__).resolve().parents[1] / "controls" / "exact_instance_review.py"
spec = importlib.util.spec_from_file_location("exact_review", src)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

B = b"synthetic attached file"
INSTANCE = {
    "instance_id":"synth1", "crm_record_id":"synth-crm1", "intent":"FINANCE_LEASE",
    "action":"SEND", "channel":"CH-EMAIL", "issuer_id":"synth-issuer",
    "sender_id":"synth-sender", "adapter_id":"approved-crm-adapter",
    "template_id":"synth-template", "template_version":"1", "template_sha256":"a"*64,
    "parent_instance_sha256":"b"*64, "subject":"Synthetic quote", "body":"Synthetic body",
    "to":["user@example.test"], "cc":[], "bcc":[],
    "attachments":[{"name":"proof.pdf","media_type":"application/pdf","sha256":sha256(B).hexdigest()}],
    "idempotency_key":"synth-idem1"
}
ATTACH={"proof.pdf": B}
def approved():
    a={k:copy.deepcopy(INSTANCE[k]) for k in mod.APPROVAL_SCOPE}
    a.update({"status":"APPROVED", "instance_sha256":mod.digest_instance(INSTANCE,ATTACH),
              "to":list(INSTANCE["to"]),"cc":[],"bcc":[], "expires_at":"2027-10-01T00:00:00+00:00",
              "receipt_id":"synth-receipt", "approver_id":"synth-approver"})
    return a
NOW=datetime(2026,10,20,tzinfo=timezone.utc)
class IntegrityTests(unittest.TestCase):
    def denied(self, inst, attachments, approval, reason):
        result=mod.review(inst,attachments,approval,NOW)
        self.assertEqual(result["decision"],"DENY")
        self.assertFalse(result["production_release_allowed"])
        self.assertIn(reason,result["reason_codes"])
    def test_nominal_never_sends(self):
        a=approved(); result=mod.review(INSTANCE,ATTACH,a,NOW)
        self.assertEqual(result["decision"],"REVIEW_ONLY")
        self.assertFalse(result["production_release_allowed"])
    def test_mutations(self):
        changes={
            "subject":"Changed", "body":"Changed", "sender_id":"different",
            "adapter_id":"unapproved", "template_version":"2",
            "idempotency_key":"other", "template_sha256":"c"*64,
            "to":["other@example.test"], "cc":["other@example.test"],
            "bcc":["other@example.test"]
        }
        for k,v in changes.items():
            with self.subTest(k=k):
                inst=copy.deepcopy(INSTANCE); inst[k]=v
                self.denied(inst,ATTACH,approved(),"APPROVED_INSTANCE_CHANGED")
    def test_changed_attachment(self):
        self.denied(INSTANCE,{"proof.pdf":b"changed"},approved(),"ATTACHMENT_BYTES_CHANGED")
    def test_missing_attachment(self):
        self.denied(INSTANCE,{},approved(),"ATTACHMENT_BYTES_CHANGED")
    def test_injected_attachment(self):
        self.denied(INSTANCE,{**ATTACH,"other.pdf":b"extra"},approved(),"ATTACHMENT_SET_CHANGED")
    def test_parent_required(self):
        inst=copy.deepcopy(INSTANCE);inst["parent_instance_sha256"]=None
        self.denied(inst,ATTACH,approved(),"PARENT_INSTANCE_REQUIRED")
    def test_expired_approval(self):
        a=approved(); a["expires_at"]="2026-01-01T00:00:00+00:00"
        self.denied(INSTANCE,ATTACH,a,"APPROVAL_EXPIRED")
    def test_self_assertion_insufficient(self):
        a=approved();a["status"]="PENDING"
        self.denied(INSTANCE,ATTACH,a,"APPROVAL_NOT_ACTIVE")
    def test_incomplete_instance(self):
        inst=copy.deepcopy(INSTANCE);del inst["sender_id"]
        self.denied(inst,ATTACH,approved(),"INSTANCE_STRUCTURE_INVALID")
if __name__=="__main__":
    unittest.main()
