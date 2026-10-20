"""Synthetic regression suite: digital twin is not a production authority."""
import importlib.util
import json
import unittest
from pathlib import Path

base = Path(__file__).resolve().parents[1] / "controls"
spec = importlib.util.spec_from_file_location("simulator", base / "simulate_twin.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
BASE = json.loads((base / "customer-communications-twin.review.json").read_text())

def candidate(**kw):
    payload = {
        "intent": "review",
        "target": dict(BASE["target"]),
        "tests_passed": True,
        "source_metadata_fresh": True,
        "deployment_approval_verified": False,
        "runtime_bypass_test_passed": False,
    }
    payload.update(kw)
    return payload

class TwinSimulationTests(unittest.TestCase):
    def assertDenied(self, twin, change, reason):
        result = mod.assess(twin, change)
        self.assertEqual(result["decision"], "HOLD")
        self.assertFalse(result["production_authorised"])
        self.assertIn(reason, result["reasons"])
    def test_source_metadata_projection(self):
        projection = json.loads((base / "zoho-communication-config-observed.review.json").read_text())
        self.assertIs(projection["business_records_embedded"], False)
        self.assertIs(projection["complete_tenant_model"], False)
        for name in ("CustomerCommunications", "Agreement_Templates", "BusinessDocumentTypes", "CustomerDocuments", "GovernedApprovals", "Quotes", "Deals"):
            self.assertIn(name, projection["observed"]["modules"])
        self.assertGreaterEqual(projection["observed"]["email_templates"]["count"], 1)
        self.assertIs(projection["observed"]["email_templates"]["publication_status_verified"], False)
        self.assertIs(projection["observed"]["profiles"]["effective_agent_permissions_verified"], False)
        self.assertIs(projection["observed"]["functions"]["release_interceptor_verified"], False)
    def test_baseline_partial(self):
        self.assertDenied(BASE, candidate(), "BASELINE_PARTIAL")
    def test_current_direct_send_unverified(self):
        self.assertDenied(BASE, candidate(), "CURRENT_SEND_PATH_UNGUARDED")
    def test_bypass_unclosed(self):
        self.assertDenied(BASE, candidate(), "CURRENT_BYPASS_UNCLOSED")
    def test_production_always_denied(self):
        self.assertDenied(BASE, candidate(intent="production"), "PRODUCTION_RELEASE_NOT_AUTHORISED")
    def test_missing_required_target(self):
        for key in mod.REQUIRED:
            with self.subTest(key=key):
                target = dict(BASE["target"])
                target[key] = False
                self.assertDenied(BASE, candidate(target=target), "MISSING_TARGET_" + key.upper())
    def test_missing_test_evidence(self):
        for key in ("tests_passed", "source_metadata_fresh", "deployment_approval_verified", "runtime_bypass_test_passed"):
            with self.subTest(key=key):
                self.assertDenied(BASE, candidate(**{key:False}), "UNVERIFIED_" + key.upper())
    def test_invalid_change_intent(self):
        self.assertDenied(BASE, candidate(intent="direct-production"), "CHANGE_INTENT_INVALID")
    def test_no_business_records(self):
        self.assertIs(BASE["source"]["contains_business_records"], False)
    def test_nominal_simulation_not_release(self):
        twin = json.loads(json.dumps(BASE))
        twin["source"]["completeness"] = "complete"
        twin["configuration"]["synchronous_send_interceptor"]["verified"] = True
        twin["configuration"]["unrestricted_agent_transport_closed"]["verified"] = True
        result = mod.assess(twin, candidate(deployment_approval_verified=True, runtime_bypass_test_passed=True))
        self.assertEqual(result["decision"], "SANDBOX_CANDIDATE_ONLY")
        self.assertFalse(result["production_authorised"])

if __name__ == "__main__":
    unittest.main()
