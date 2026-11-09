"""Synthetic CRM boundary tests."""
import unittest
from dataclasses import replace
from identity_validation.crm_adapter import plan_contact_update, validate_slot
from identity_validation.enrollment import EnrollmentEvidence
from identity_validation.validator import Status


class CRMBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.evidence = EnrollmentEvidence(
            identity_status=Status.MANUAL_REVIEW_REQUIRED,
            enterprise_terms_accepted=False, access_terms_accepted=False,
            access_approved=False, slot_approved=False,
            keypad_programmed=False, delivery_confirmed=False,
        )

    def test_pending_is_not_active(self):
        plan = plan_contact_update(contact_id="synthetic", expected_version="v1",
                                   evidence=self.evidence, current_identity_status="PENDING")
        self.assertTrue(plan.requires_review)
        self.assertEqual(plan.fields["Onboarding_State"], "IDENTITY_REVIEW")

    def test_reject_silent_downgrade(self):
        with self.assertRaises(ValueError):
            plan_contact_update(contact_id="synthetic", expected_version="v1",
                                evidence=self.evidence, current_identity_status="VERIFIED")

    def test_missing_version(self):
        with self.assertRaises(ValueError):
            plan_contact_update(contact_id="synthetic", expected_version="",
                                evidence=self.evidence, current_identity_status="PENDING")

    def test_slot_policy(self):
        self.assertTrue(validate_slot(200))
        self.assertTrue(validate_slot(219))
        self.assertFalse(validate_slot(100))
        self.assertFalse(validate_slot(220))
        self.assertFalse(validate_slot(True))


if __name__ == "__main__":
    unittest.main()
