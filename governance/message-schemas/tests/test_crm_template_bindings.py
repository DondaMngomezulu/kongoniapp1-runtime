#!/usr/bin/env python3
"""Synthetic-only regression checks for the 5 registered bindings and fail-closed mapping rules."""
import copy, json, pathlib
from jsonschema import Draft202012Validator, FormatChecker
ROOT=pathlib.Path(__file__).resolve().parents[1]
schema=json.loads((ROOT/"schemas/crm-template-binding.candidate.schema.json").read_text())
data=json.loads((ROOT/"tests/fixtures/synthetic-message-bindings.json").read_text())
Draft202012Validator.check_schema(schema)
v=Draft202012Validator(schema,format_checker=FormatChecker())
assert len(data)==5 and {x["bindingId"] for x in data}=={"SB-0001","SB-0002","SB-0003","SB-0004","SB-0006"}
for row in data:
    assert not list(v.iter_errors(row))
    assert row["releaseGate"]=="BLOCKED_PENDING_RUNTIME_AND_APPROVAL"
    missing=copy.deepcopy(row);del missing["schemaId"]
    assert not v.is_valid(missing)
    unsafe=copy.deepcopy(row);unsafe["releaseGate"]="PRODUCTION_ENABLED"
    assert not v.is_valid(unsafe)
    wrong=copy.deepcopy(row);wrong["mappingKind"]="UNKNOWN"
    assert not v.is_valid(wrong)
    extra=copy.deepcopy(row);extra["customerPersonalData"]="never store"
    assert not v.is_valid(extra)
# Native lookup is not a text key; identity resolver is distinct from native lookup.
types={"NATIVE_LOOKUP":{"lookup"},"IDENTITY_RESOLVER":{"text","autonumber"},"DIRECT_SCALAR":{"text","textarea","date","datetime","currency","double","integer","boolean","picklist"},"SUBFORM":{"subform"}}
for row in data:
    if row["mappingKind"] in types:
        assert row["observedFieldType"] in types[row["mappingKind"]]
assert not any(row["crmField"]=="Registration_Date" for row in data)
print("PASS: five synthetic source bindings; required, fail-closed, mapping enum, extra-data and field-kind checks")
