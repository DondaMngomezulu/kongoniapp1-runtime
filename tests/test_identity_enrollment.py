"""State machine tests use synthetic evidence, no employee details."""
import unittest
from dataclasses import replace
from identity_validation.validator import Status
from identity_validation.enrollment import EnrollmentEvidence, EnrollmentState, derive_state, crm_projection


class EnrollmentTests(unittest.TestCase):
    def setUp(self):
        self.ready = EnrollmentEvidence(
            identity_status=Status.VERIFIED,
            enterprise_terms_accepted=True, access_terms_accepted=True,
            access_approved=True, slot_approved=True,
            keypad_programmed=True, delivery_confirmed=True,
        )

    def test_all_gates_required(self):
        self.assertEqual(derive_state(self.ready), EnrollmentState.ACTIVE)

    def test_identity_pending(self):
        self.assertEqual(derive_state(replace(self.ready, identity_status=Status.MANUAL_REVIEW_REQUIRED)), EnrollmentState.IDENTITY_REVIEW)

    def test_terms_pending(self):
        self.assertEqual(derive_state(replace(self.ready, enterprise_terms_accepted=False)), EnrollmentState.TERMS_PENDING)
        self.assertEqual(derive_state(replace(self.ready, access_terms_accepted=False)), EnrollmentState.TERMS_PENDING)

    def test_approval_pending(self):
        self.assertEqual(derive_state(replace(self.ready, access_approved=False)), EnrollmentState.ACCESS_APPROVAL_PENDING)
        self.assertEqual(derive_state(replace(self.ready, slot_approved=False)), EnrollmentState.ACCESS_APPROVAL_PENDING)

    def test_keypad_and_delivery(self):
        self.assertEqual(derive_state(replace(self.ready, keypad_programmed=False)), EnrollmentState.ACCESS_PROVISIONING_PENDING)
        self.assertEqual(derive_state(replace(self.ready, delivery_confirmed=False)), EnrollmentState.ACCESS_PROVISIONING_PENDING)

    def test_expired_code(self):
        self.assertEqual(derive_state(replace(self.ready, code_expired=True)), EnrollmentState.ACCESS_PROVISIONING_PENDING)

    def test_rejected(self):
        self.assertEqual(derive_state(replace(self.ready, identity_status=Status.REJECTED)), EnrollmentState.REJECTED)

    def test_crm_projection(self):
        self.assertEqual(crm_projection(replace(self.ready, identity_status=Status.PENDING))["ID_Verification_Status"], "PENDING")


if __name__ == "__main__":
    unittest.main()
