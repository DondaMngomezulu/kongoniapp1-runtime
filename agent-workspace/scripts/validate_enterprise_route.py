#!/usr/bin/env python3
"""Fail closed on missing PR route metadata and unmanifested enterprise configuration changes."""
import json, os, re, subprocess, sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

def fail(message):
    print("CTL-ENG-GH-ROUTE-001 FAIL:", message)
    sys.exit(1)

control = Path("governance/controls/CTL-ENG-GH-ROUTE-001.yaml")
if not control.exists():
    fail("control document missing")
policy = yaml.safe_load(control.read_text())
if policy.get("control_id") != "CTL-ENG-GH-ROUTE-001":
    fail("incorrect control ID")
schema_path = Path("governance/schemas/configuration-change.schema.json")
schema = json.loads(schema_path.read_text())
validator = Draft202012Validator(schema)
if os.getenv("EVENT_NAME") == "pull_request":
    body = os.getenv("PR_BODY") or ""
    required = {
        "issue": r"(https://github\.com/[^\s]+/issues/\d+|(?:Refs|Closes|Fixes)\s+#\d+)",
        "route": r"(?im)^Route-ID:\s*\S+",
        "task class": r"(?im)^Task-Class:\s*T[0-3]\b",
        "change class": r"(?im)^Change-Class:\s*\S+",
        "target system": r"(?im)^Target-System:\s*\S+",
        "target environment": r"(?im)^Target-Environment:\s*\S+",
        "authority": r"(?im)^Authority-Ref:\s*\S+",
        "verification plan": r"(?im)^Verification-Plan:\s*\S+",
    }
    for label, pattern in required.items():
        if not re.search(pattern, body):
            fail("PR missing " + label)
    base, head = os.getenv("BASE_SHA"), os.getenv("HEAD_SHA")
    if not base or not head:
        fail("PR diff SHA context absent")
    changed = subprocess.check_output(["git", "diff", "--name-only", base + "..." + head], text=True).splitlines()
    non_config = ["README.md", "AGENTS.md", ".github/PULL_REQUEST_TEMPLATE.md", "agent-workspace/AGENTS.md"]
    config_paths = [p for p in changed if p not in non_config and not p.startswith("agent-workspace/change-log/") and not p.startswith("governance/configuration-changes/") and not p.startswith("governance/schemas/")]
    if config_paths:
        manifests = [p for p in changed if re.fullmatch(r"governance/configuration-changes/CFG-[A-Za-z0-9-]+\.ya?ml", p)]
        if not manifests:
            fail("material change missing configuration change manifest")
        covered = set()
        for path in manifests:
            p = Path(path)
            if not p.exists():
                fail("configuration manifest missing from PR head: " + path)
            data = yaml.safe_load(p.read_text())
            errors = list(validator.iter_errors(data))
            if errors:
                fail(path + ": " + "; ".join(x.message for x in errors))
            if data.get("approval_state") == "DEPLOYED_VERIFIED" and not (data.get("native_audit_ref") and data.get("run_id")):
                fail(path + " claims deployed without execution receipts")
            covered.update(data["affected_paths"])
        uncovered = set(config_paths).difference(covered)
        if uncovered:
            fail("configuration manifest lacks affected_paths: " + ", ".join(sorted(uncovered)))
else:
    # Push-side CI checks the policy contract only. GitHub branch rules are required to block direct pushes.
    print("Push event; authoritative enforcement requires main branch ruleset")
print("CTL-ENG-GH-ROUTE-001 PASS (repository route metadata only; not target-system deployment authority)")
