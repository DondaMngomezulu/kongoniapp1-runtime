"""Review-only system configuration twin simulation. Never issues or deploys."""
import json
from pathlib import Path

REQUIRED = (
    "approved_template_or_scoped_instance", "exact_approval_and_content_digest",
    "synchronous_gate_before_transport", "agent_bypass_routes_denied",
    "immutable_evidence_and_idempotency",
)

def assess(twin, change):
    reasons = []
    if twin.get("source", {}).get("completeness") != "complete":
        reasons.append("BASELINE_PARTIAL")
    current = twin.get("configuration", {})
    if not current.get("synchronous_send_interceptor", {}).get("verified"):
        reasons.append("CURRENT_SEND_PATH_UNGUARDED")
    if not current.get("unrestricted_agent_transport_closed", {}).get("verified"):
        reasons.append("CURRENT_BYPASS_UNCLOSED")
    if change.get("intent") not in ("review", "sandbox", "production"):
        reasons.append("CHANGE_INTENT_INVALID")
    if change.get("intent") == "production":
        reasons.append("PRODUCTION_RELEASE_NOT_AUTHORISED")
    proposed = change.get("target", {})
    for item in REQUIRED:
        if proposed.get(item) is not True:
            reasons.append("MISSING_TARGET_" + item.upper())
    for item in ("tests_passed", "source_metadata_fresh", "deployment_approval_verified", "runtime_bypass_test_passed"):
        if change.get(item) is not True:
            reasons.append("UNVERIFIED_" + item.upper())
    return {
        "decision": "HOLD" if reasons else "SANDBOX_CANDIDATE_ONLY",
        "reasons": sorted(set(reasons)),
        "production_authorised": False,
    }

if __name__ == "__main__":
    base = Path(__file__).parent
    twin = json.loads((base / "customer-communications-twin.review.json").read_text())
    candidate = {
        "intent": "review", "target": twin["target"], "tests_passed": True,
        "source_metadata_fresh": True, "deployment_approval_verified": False,
        "runtime_bypass_test_passed": False,
    }
    result = assess(twin, candidate)
    print(json.dumps(result, indent=2))
    assert result["decision"] == "HOLD"
    assert "CURRENT_SEND_PATH_UNGUARDED" in result["reasons"]
    assert "CURRENT_BYPASS_UNCLOSED" in result["reasons"]
    assert not assess(twin, {**candidate, "intent":"production"})["production_authorised"]
    assert "MISSING_TARGET_APPROVED_TEMPLATE_OR_SCOPED_INSTANCE" in assess(twin, {**candidate, "target": {}})["reasons"]
    print("PASS: partial baseline, bypass, missing template and production hold scenarios")
