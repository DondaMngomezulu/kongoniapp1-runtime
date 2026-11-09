"""Synthetic tests for intake safety and fail-closed behaviour."""
import unittest
from identity_validation.orchestrator import process_document, detect_mime
from identity_validation.validator import Status


class StubExtractor:
    def __init__(self, fields):
        self.fields = fields
    def extract(self, content, mime, document_type):
        return self.fields


class StubProvider:
    def __init__(self, result):
        self.result = result
    def verify(self, **kwargs):
        return self.result


class IntakeTests(unittest.TestCase):
    def run_doc(self, **kwargs):
        defaults = dict(
            content=b"%PDF-1.7\nsynthetic",
            document_type="DRIVERS_LICENCE", contact_id="synthetic-contact",
            dedupe_secret=b"test-only-secret", extractor=StubExtractor({"licence_number": "SYNTHETIC"}),
            authority=None, consent_recorded=True, crm_identity_match=True,
        )
        defaults.update(kwargs)
        return process_document(**defaults)

    def test_unknown_file(self):
        with self.assertRaises(ValueError):
            self.run_doc(content=b"not-a-document")

    def test_no_extractor(self):
        self.assertEqual(self.run_doc(extractor=None).status, Status.MANUAL_REVIEW_REQUIRED)

    def test_no_consent(self):
        self.assertEqual(self.run_doc(consent_recorded=False).reason, "consent_not_recorded")

    def test_no_provider(self):
        self.assertEqual(self.run_doc().reason, "authoritative_provider_not_configured")

    def test_untrusted_provider(self):
        provider = StubProvider({"identity_match": True, "document_authenticity": True})
        self.assertEqual(self.run_doc(authority=provider).reason, "provider_evidence_untrusted")

    def test_authenticated_provider_requires_crm_match(self):
        provider = StubProvider({
            "evidence_authenticated": True, "identity_match": True,
            "document_authenticity": True, "reference": "synthetic-ref"
        })
        self.assertEqual(self.run_doc(authority=provider, crm_identity_match=None).status,
                         Status.MANUAL_REVIEW_REQUIRED)

    def test_authenticated_provider_complete(self):
        provider = StubProvider({
            "evidence_authenticated": True, "identity_match": True,
            "document_authenticity": True, "reference": "synthetic-ref"
        })
        self.assertEqual(self.run_doc(authority=provider).status, Status.VERIFIED)


if __name__ == "__main__":
    unittest.main()
