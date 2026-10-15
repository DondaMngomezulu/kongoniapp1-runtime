import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("message_profiles", ROOT / "scripts/message_profiles.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MessageProfiles(unittest.TestCase):
    def setUp(self):
        self.event = json.loads((ROOT / "fixtures/information-request.synthetic.json").read_text())

    def fails(self, mutate):
        mutate(self.event)
        with self.assertRaises((ValueError, ValidationError)):
            module.prepare_preview(self.event)

    def test_valid_native_projections(self):
        result = module.prepare_preview(self.event)
        self.assertEqual(result["tmf681"]["messageType"], "Email")
        self.assertEqual(result["bianOutbound"]["CorrespondenceRecord"]["CorrespondenceMedium"], "Electronic")
        self.assertFalse(result["dispatchEnabled"])
        self.assertEqual(result["profile"]["approvalStatus"], "PENDING")

    def test_preserves_input_and_unknowns(self):
        before = copy.deepcopy(self.event)
        module.prepare_preview(self.event)
        self.assertEqual(self.event, before)
        for field in ("financingMethod", "financePreApproval", "purchasingEntity"):
            self.assertIsNone(self.event["data"][field])

    def test_no_fabricated_deadline_or_response(self):
        result = module.prepare_preview(self.event)
        self.assertEqual(result["bianOutboundWithResponse"], {})
        self.assertNotIn("sendTime", result["tmf681"])
        self.assertNotIn("state", result["tmf681"])

    def test_supported_due_date(self):
        self.event["data"]["responseDueDate"] = "2000-02-01T12:00:00Z"
        result = module.prepare_preview(self.event)
        self.assertEqual(result["bianOutboundWithResponse"]["ResponseDueDate"]["DateTimeContent"],
                         "2000-02-01T12:00:00Z")

    def test_invalid_deadline(self):
        self.fails(lambda x: x["data"].update(responseDueDate="tomorrow"))

    def test_unverified_finance_claims_rejected(self):
        for key, value in (("financingMethod", "cash"), ("financePreApproval", True),
                           ("purchasingEntity", "Invented Company")):
            with self.subTest(key=key):
                event = copy.deepcopy(self.event)
                event["data"][key] = value
                with self.assertRaises(ValidationError):
                    module.prepare_preview(event)

    def test_sensitive_extra_fields_rejected(self):
        self.fails(lambda x: x["data"].update(bankAccountNumber="sensitive-example"))

    def test_unknown_profile(self):
        self.fails(lambda x: x["schema"].update(id="unsupported"))

    def test_unknown_version(self):
        self.fails(lambda x: x["schema"].update(version="latest"))

    def test_payload_profile_version_mismatch(self):
        self.fails(lambda x: x["data"]["profile"].update(version="99.0.0"))

    def test_reference_mismatch(self):
        self.fails(lambda x: x["subject"].update(objectId="different"))

    def test_missing_idempotency(self):
        self.fails(lambda x: x.pop("idempotencyKey"))

    def test_missing_actor(self):
        self.fails(lambda x: x.pop("actor"))

    def test_bad_recipient(self):
        self.fails(lambda x: x["data"]["to"][0].update(email="invalid-address"))

    def test_empty_recipients(self):
        self.fails(lambda x: x["data"].update(to=[]))

    def test_html_escaped(self):
        self.event["data"]["introduction"] = '<script>alert("example")</script>'
        content = module.prepare_preview(self.event)["tmf681"]["content"]
        self.assertNotIn("<script>", content)
        self.assertIn("&lt;script&gt;", content)

    def test_cc_roles_retained(self):
        cc = {"name": "Example Reviewer", "email": "reviewer@example.invalid"}
        self.event["data"]["cc"] = [cc]
        result = module.prepare_preview(self.event)
        self.assertEqual(result["transport"]["cc"], [cc])
        self.assertEqual(result["tmf681"]["receiver"], self.event["data"]["to"] + [cc])

    def test_duplicate_preparation_is_deterministic(self):
        # Preparation has no side effects. Runtime duplicate-send prevention remains unimplemented.
        self.assertEqual(module.prepare_preview(self.event), module.prepare_preview(self.event))

    def test_no_approval_from_actor_claim(self):
        self.event["actor"]["authorityRef"] = "unverified-self-assertion"
        result = module.prepare_preview(self.event)
        self.assertFalse(result["dispatchEnabled"])
        self.assertEqual(result["profile"]["approvalStatus"], "PENDING")

    def test_pinned_source_corruption_rejected(self):
        original = module.ROOT
        with tempfile.TemporaryDirectory() as d:
            import shutil
            shutil.copytree(ROOT / "sources", Path(d) / "sources")
            module.ROOT = Path(d)
            try:
                p = module.ROOT / "sources/bian/14.0.0/Correspondence.yaml"
                p.write_bytes(p.read_bytes() + b"\n# changed")
                with self.assertRaisesRegex(ValueError, "digest mismatch"):
                    module.verify_sources()
            finally:
                module.ROOT = original

    def test_unsupported_acord_projection_rejected(self):
        with self.assertRaisesRegex(ValueError, "licensed ACORD"):
            module._native_validate({}, "ACORD", "Policy")

    def test_native_tmf_missing_sender_rejected(self):
        with self.assertRaises(ValidationError):
            module._native_validate({"content":"test","receiver":[{"email":"a@example.invalid"}],
                                     "messageType":"Email"}, "TMF681", "CommunicationMessage_Create")

    def test_native_bian_invalid_medium_rejected(self):
        with self.assertRaises(ValidationError):
            module._native_validate({"CorrespondenceRecord":{"CorrespondenceMedium":"Unknown"}},
                                    "BIAN", "Outbound")


if __name__ == "__main__":
    unittest.main()
