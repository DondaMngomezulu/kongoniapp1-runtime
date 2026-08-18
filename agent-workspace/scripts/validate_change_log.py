#!/usr/bin/env python3
import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

LOG_PREFIX = "agent-workspace/change-log/"
EXEMPT_PATTERNS = [
    "agent-workspace/change-log/**",
    ".github/workflows/change-log-control.yml",
    "agent-workspace/scripts/validate_change_log.py",
    "agent-workspace/schemas/change-log.schema.json",
    "agent-workspace/templates/change-log-entry.yaml",
    "agent-workspace/governance/CTL-DEV-CHG-LOG-001.yaml",
]


def git_changed_files(base: str, head: str):
    out = subprocess.check_output(
        ["git", "diff", "--name-only", f"{base}...{head}"], text=True
    )
    return [line.strip() for line in out.splitlines() if line.strip()]


def exempt(path: str) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in EXEMPT_PATTERNS)


def load_schema():
    return json.loads(Path("agent-workspace/schemas/change-log.schema.json").read_text())


def validate_entry(path: str, validator):
    data = yaml.safe_load(Path(path).read_text())
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    messages = [f"{path}: {err.message}" for err in errors]

    if isinstance(data, dict):
        pdca = data.get("pdca", {}) or {}
        task_class = data.get("task_class")
        if task_class in {"T2", "T3"} and pdca.get("task_complete"):
            if not pdca.get("check_study_result"):
                messages.append(f"{path}: T2/T3 task_complete requires check_study_result")
            if pdca.get("act_decision") not in {"ADOPT", "ADAPT", "REPEAT", "REJECT", "ESCALATE"}:
                messages.append(f"{path}: T2/T3 task_complete requires valid act_decision")
        if pdca.get("task_complete") and not pdca.get("do_complete"):
            messages.append(f"{path}: task_complete cannot be true when do_complete is false")

    return data, messages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args()

    changed = git_changed_files(args.base, args.head)
    protected = [p for p in changed if not exempt(p)]
    logs = [p for p in changed if p.startswith(LOG_PREFIX) and p.endswith((".yaml", ".yml"))]

    if not protected:
        print("No protected changes detected; change-log record not required.")
        return 0

    if not logs:
        print("ERROR: protected repository changes require a same-change-set change-log entry.")
        print("Protected paths:")
        for p in protected:
            print(f"  - {p}")
        return 1

    validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    all_errors = []
    covered = set()

    for log in logs:
        data, errors = validate_entry(log, validator)
        all_errors.extend(errors)
        if isinstance(data, dict):
            for p in data.get("affected_paths", []) or []:
                covered.add(p)

    uncovered = [p for p in protected if p not in covered]
    if uncovered:
        all_errors.append(
            "Change-log affected_paths do not cover all protected changes: " + ", ".join(uncovered)
        )

    if all_errors:
        print("ERROR: CTL-DEV-CHG-LOG-001 validation failed")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"CTL-DEV-CHG-LOG-001 passed: {len(protected)} protected path(s), {len(logs)} log record(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
