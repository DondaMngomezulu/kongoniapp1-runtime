"""Unit tests use synthetic identifiers only."""
import unittest
from identity_validation.validator import Status, ValidationResult, validate_sa_id, decision, intake_key


class ValidationTests(unittest.TestCase):
    def test_bad_format(self):
        self.assertEqual(validate_sa_id("123").status, Status.REJECTED)

    def test_invalid_date(self):
        self.assertEqual(validate_sa_id("9913321234088").status, Status.REJECTED)

    def test_invalid_checksum(self):
        self.assertEqual(validate_sa_id("0001015009088").status, Status.REJECTED)

    def test_no_authoritative_evidence(self):
        structural = ValidationResult(Status.MANUAL_REVIEW_REQUIRED, {"checksum": True}, "structural")
        self.assertEqual(decision(structural, None, None, True).status, Status.MANUAL_REVIEW_REQUIRED)

    def test_provider_rejection(self):
        structural = ValidationResult(Status.MANUAL_REVIEW_REQUIRED, {"checksum": True}, "structural")
        self.assertEqual(decision(structural, False, True, True).status, Status.REJECTED)

    def test_complete_positive_evidence(self):
        structural = ValidationResult(Status.MANUAL_REVIEW_REQUIRED, {"checksum": True}, "structural")
        self.assertEqual(decision(structural, True, True, True).status, Status.VERIFIED)

    def test_deduplication(self):
        self.assertEqual(intake_key(b"secret", b"document", "contact"), intake_key(b"secret", b"document", "contact"))
        self.assertNotEqual(intake_key(b"secret", b"document", "contact"), intake_key(b"secret", b"other", "contact"))


if __name__ == "__main__":
    unittest.main()
