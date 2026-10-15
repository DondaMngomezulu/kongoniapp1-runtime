"""Pre-adoption adversarial and integrity regression tests; synthetic data only."""
import copy
from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
import shutil
import socket
import tempfile
import unittest
from unittest.mock import patch

from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("adoption_profiles", ROOT / "scripts/message_profiles.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PreAdoption(unittest.TestCase):
    def setUp(self):
        self.event = json.loads((ROOT / "fixtures/information-request.synthetic.json").read_text())

    def rejects(self, event):
        with self.assertRaises((ValueError, ValidationError)):
            module.prepare_preview(event)

    @contextmanager
    def package(self):
        original = module.ROOT
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "package"
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("__pycache__"))
            module.ROOT = target
            try:
                yield target
            finally:
                module.ROOT = original

    def test_malformed_inputs_have_controlled_errors(self):
        for value in (None, [], "", 3, {"schema": None}, {"schema": []}, {"schema": "wrong"}):
            with self.subTest(value=value):
                self.rejects(value)

    def test_header_linebreaks_rejected(self):
        for header in ("subject", "sender-name", "sender-email", "receiver-name", "receiver-email"):
            for control in ("\r", "\n", "\x00", "\x7f"):
                with self.subTest(header=header, control=repr(control)):
                    event = copy.deepcopy(self.event)
                    if header == "subject":
                        event["data"]["subject"] += control + "Bcc: injected@example.invalid"
                    else:
                        party = event["data"]["sender"] if header.startswith("sender") else event["data"]["to"][0]
                        party["name" if header.endswith("name") else "email"] += control + "injected@example.invalid"
                    self.rejects(event)

    def test_bare_mailbox_syntax_required(self):
        for email in ("a@b@c", "@", "name <a@example.invalid>", "a@example.invalid,b@example.invalid",
                      "a b@example.invalid", " a@example.invalid ", "a@", "@example.invalid"):
            with self.subTest(email=email):
                event = copy.deepcopy(self.event)
                event["data"]["to"][0]["email"] = email
                self.rejects(event)

    def test_international_display_name_supported(self):
        self.event["data"]["sender"]["name"] = "Zoë Mokoena"
        self.assertIn("Zoë", module.prepare_preview(self.event)["tmf681"]["content"])

    def test_duplicate_recipients_rejected(self):
        for position in ("same-list", "to-cc", "domain-case"):
            with self.subTest(position=position):
                event = copy.deepcopy(self.event)
                recipient = copy.deepcopy(event["data"]["to"][0])
                if position == "domain-case":
                    local, domain = recipient["email"].rsplit("@", 1)
                    recipient["email"] = local + "@" + domain.upper()
                if position == "same-list":
                    event["data"]["to"].append(recipient)
                else:
                    event["data"]["cc"].append(recipient)
                self.rejects(event)

    def test_whitespace_only_material_fields_rejected(self):
        for field in ("reference", "subject", "introduction"):
            event = copy.deepcopy(self.event)
            event["data"][field] = "   "
            if field == "reference":
                event["subject"]["objectId"] = "   "
            with self.subTest(field=field):
                self.rejects(event)
        for field in ("name", "email"):
            event = copy.deepcopy(self.event)
            event["data"]["sender"][field] = "   "
            self.rejects(event)
        event = copy.deepcopy(self.event)
        event["data"]["requestedItems"][0]["description"] = " \t "
        self.rejects(event)

    def test_unresolved_template_tokens_rejected(self):
        for token in ("{{Recipient_First_Name}}", "${Recipient.Name}", "{{unfinished"):
            with self.subTest(token=token):
                event = copy.deepcopy(self.event)
                event["data"]["introduction"] = token
                self.rejects(event)

    def test_schema_reference_bound_to_profile(self):
        event = copy.deepcopy(self.event)
        event["schema"]["uri"] = "https://untrusted.example.invalid/another-schema"
        self.rejects(event)

    def test_empty_source_manifest_rejected(self):
        with self.package() as root:
            p = root / "sources/manifest.json"
            manifest = json.loads(p.read_text())
            manifest["files"] = []
            p.write_text(json.dumps(manifest))
            self.rejects(self.event)

    def test_missing_required_manifest_entry_rejected(self):
        with self.package() as root:
            p = root / "sources/manifest.json"
            manifest = json.loads(p.read_text())
            manifest["files"].pop()
            p.write_text(json.dumps(manifest))
            self.rejects(self.event)

    def test_duplicate_manifest_entry_rejected(self):
        with self.package() as root:
            p = root / "sources/manifest.json"
            manifest = json.loads(p.read_text())
            manifest["files"].append(copy.deepcopy(manifest["files"][0]))
            p.write_text(json.dumps(manifest))
            self.rejects(self.event)

    def test_source_and_manifest_rehash_cannot_replace_pinned_release(self):
        import hashlib
        with self.package() as root:
            manifest_path = root / "sources/manifest.json"
            manifest = json.loads(manifest_path.read_text())
            entry = manifest["files"][0]
            p = root / entry["path"]
            p.write_bytes(p.read_bytes() + b"\n# changed source")
            entry["sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest))
            self.rejects(self.event)

    def test_wrong_source_version_rejected(self):
        with self.package() as root:
            p = root / "sources/manifest.json"
            manifest = json.loads(p.read_text())
            manifest["files"][0]["version"] = "99.0.0"
            p.write_text(json.dumps(manifest))
            self.rejects(self.event)

    def test_registry_cannot_relabel_native_bindings(self):
        for attribute, value in (("version", "99.0.0"), ("source", "sources/other.json"),
                                 ("component", "NotTheValidatedComponent")):
            with self.subTest(attribute=attribute), self.package() as root:
                p = root / "profiles/registry.candidate.json"
                registry = json.loads(p.read_text())
                registry["profiles"][0]["standards"][0][attribute] = value
                p.write_text(json.dumps(registry))
                self.rejects(self.event)

    def test_ambiguous_profile_rejected(self):
        with self.package() as root:
            p = root / "profiles/registry.candidate.json"
            registry = json.loads(p.read_text())
            registry["profiles"].append(copy.deepcopy(registry["profiles"][0]))
            p.write_text(json.dumps(registry))
            self.rejects(self.event)

    def test_traversal_manifest_entry_rejected(self):
        with self.package() as root:
            p = root / "sources/manifest.json"
            manifest = json.loads(p.read_text())
            manifest["files"][0]["path"] = "../outside"
            p.write_text(json.dumps(manifest))
            self.rejects(self.event)

    def test_duplicate_json_keys_rejected(self):
        with self.package() as root:
            p = root / "profiles/registry.candidate.json"
            p.write_text(p.read_text().replace('"status": "CANDIDATE_REVIEW"',
                                              '"status": "CANDIDATE_REVIEW", "status": "APPROVED"'))
            self.rejects(self.event)

    def test_missing_format_validation_fails_closed(self):
        # Simulate an installation missing optional date-time checker dependencies.
        with patch.dict(module.FormatChecker.checkers, clear=True):
            with self.assertRaisesRegex(ValueError, "format"):
                module.prepare_preview(self.event)

    def test_approval_metadata_cannot_enable_dispatch(self):
        with self.package() as root:
            p = root / "profiles/registry.candidate.json"
            registry = json.loads(p.read_text())
            registry["profiles"][0].update(approvalStatus="APPROVED", runtimeEnabled=True)
            p.write_text(json.dumps(registry))
            self.assertFalse(module.prepare_preview(self.event)["dispatchEnabled"])

    def test_preview_does_not_use_network(self):
        with patch.object(socket, "socket", side_effect=AssertionError("Network used")):
            self.assertFalse(module.prepare_preview(self.event)["dispatchEnabled"])

    def test_sender_recipient_and_content_mapping_agree(self):
        cc = {"name": "Example Copy", "email": "copy@example.invalid"}
        self.event["data"]["cc"] = [cc]
        result = module.prepare_preview(self.event)
        self.assertEqual(result["tmf681"]["sender"], self.event["data"]["sender"])
        self.assertEqual(result["tmf681"]["receiver"], self.event["data"]["to"] + [cc])
        self.assertEqual(result["tmf681"]["content"], result["bianOutbound"]["CorrespondenceContent"])
        self.assertEqual(result["bianOutbound"]["CorrespondenceSourceReference"], self.event["eventId"])

    def test_tmf_and_bian_generated_payloads_check_declared_fields(self):
        # Complements native schemas that allow unknown additional properties.
        import yaml
        result = module.prepare_preview(self.event)
        tmf = json.loads((ROOT / "sources/tmforum/4.0.0/TMF681.swagger.json").read_text())
        bian = yaml.safe_load((ROOT / "sources/bian/14.0.0/Correspondence.yaml").read_text())
        self.assertLessEqual(set(result["tmf681"]),
                             set(tmf["definitions"]["CommunicationMessage_Create"]["properties"]))
        self.assertLessEqual(set(result["bianOutbound"]),
                             set(bian["components"]["schemas"]["Outbound"]["properties"]))


if __name__ == "__main__":
    unittest.main()
