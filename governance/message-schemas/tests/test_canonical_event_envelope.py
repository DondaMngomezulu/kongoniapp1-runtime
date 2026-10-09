#!/usr/bin/env python3
"""Deterministic schema checks; run locally or in CI; no network access."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "schemas" / "canonical-event-envelope.candidate.schema.json").open() as fh:
    schema = json.load(fh)
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema, format_checker=FormatChecker())
good = {
    "eventId":"bba5613a-5cd4-49a7-b207-edfa3cd51f3b",
    "eventType":"example.object.created",
    "occurredAt":"2026-10-09T08:00:00Z",
    "producer":{"system":"sandbox","service":"test-emitter","environment":"development"},
    "subject":{"objectType":"Example","objectId":"fixture-001"},
    "schema":{"id":"example.fixture","version":"1.0.0","uri":"https://example.invalid/schemas/example.json"},
    "correlationId":"corr-001","data":{"name":"sample"}}
assert validator.is_valid(good), list(validator.iter_errors(good))
for field in ("eventId","eventType","occurredAt","producer","subject","schema","correlationId","data"):
    invalid = {k:v for k,v in good.items() if k != field}
    assert not validator.is_valid(invalid), "Missing field should fail: "+field
invalid = {**good, "eventId":"not-a-uuid"}
assert not validator.is_valid(invalid), "Invalid event ID passed"
invalid = {**good, "occurredAt":"yesterday"}
assert not validator.is_valid(invalid), "Invalid timestamp passed"
invalid = {**good, "producer":{**good["producer"],"unknown":"bad"}}
assert not validator.is_valid(invalid), "Unknown producer property passed"
invalid = {**good, "unexpected":"bad"}
assert not validator.is_valid(invalid), "Unknown envelope property passed"
print("PASS: valid fixture, eight missing-required-field cases, UUID, timestamp, producer unknown, envelope unknown = 13 checks.")
