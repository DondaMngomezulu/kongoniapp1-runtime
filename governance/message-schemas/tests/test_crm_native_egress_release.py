"""Reject release based only on metadata or simulation."""
import json
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"controls"/"crm-native-egress-implementation.review.json"
class CRMNativeReleaseTests(unittest.TestCase):
    def test_runtime_hold(self):
        d=json.loads(P.read_text())
        self.assertEqual(d["status"],"BLOCKED_DEVELOPMENT_DESIGN")
        self.assertFalse(d["release"]["production_enabled"])
        self.assertFalse(d["release"]["production_authorised"])
        self.assertFalse(d["release"]["development_configuration_write"])
        self.assertFalse(d["observed"]["unique_reservation_constraint_verified"])
    def test_all_adapter_gates_unverified(self):
        d=json.loads(P.read_text())
        self.assertGreaterEqual(len(d["design_candidate"]["components"]),7)
        for component in d["design_candidate"]["components"]:
            self.assertEqual(component["status"],"UNVERIFIED")
        self.assertFalse(d["evidence_gates"]["provider_channel_acl_verified"])
        self.assertFalse(d["evidence_gates"]["crm_unique_reservation_verified"])
        self.assertFalse(d["evidence_gates"]["real_negative_tests_passed"])
    def test_twin_observed_not_business_records(self):
        d=json.loads(P.read_text())
        self.assertEqual(d["authorities"]["runtime"],"Zoho CRM")
        self.assertEqual(d["authorities"]["governance"],"GitHub Digital Twin")
if __name__=="__main__":
    unittest.main()
