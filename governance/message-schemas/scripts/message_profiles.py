"""Offline candidate message preparation. No network, dispatch or approval mutation."""
import copy
import hashlib
import html
import json
from pathlib import Path

import yaml
from jsonschema import Draft4Validator, Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]


def _json(path):
    return json.loads(path.read_text())


def _profile(key, version):
    registry = _json(ROOT / "profiles/registry.candidate.json")
    matches = [p for p in registry["profiles"] if p["key"] == key and p["version"] == version]
    if len(matches) != 1:
        raise ValueError("Unknown or ambiguous profile/version")
    return matches[0]


def verify_sources():
    manifest = _json(ROOT / "sources/manifest.json")
    for item in manifest["files"]:
        path = (ROOT / item["path"]).resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise ValueError("Source path escapes package")
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Pinned source digest mismatch: " + item["path"])


def _validate_local(envelope):
    schemas = {}
    registry = Registry()
    for path in (ROOT / "schemas").glob("*.json"):
        schema = _json(path)
        Draft202012Validator.check_schema(schema)
        # File identity is local resolver context, not a canonical enterprise URI.
        schema["$id"] = path.as_uri()
        schemas[path.name] = schema
        registry = registry.with_resource(path.as_uri(), Resource.from_contents(schema))
    validator = Draft202012Validator(
        schemas["reusable-message-envelope.candidate.schema.json"],
        registry=registry, format_checker=FormatChecker())
    validator.validate(envelope)


def render_message(data):
    """Render only schema-validated input through prepare_preview."""
    esc = html.escape
    paras = [f'<p>Dear {esc(", ".join(p["name"] for p in data["to"]))},</p>',
             f'<p>{esc(data["introduction"])}</p>',
             f'<p>Reference: {esc(data["reference"])}</p>',
             '<p>Please provide the following initial information:</p><ul>']
    paras += [f'<li>{esc(item["description"])} ({esc(item["disclosure"].lower())})</li>'
              for item in data["requestedItems"]]
    paras += ['</ul>']
    if data["confidentiality"] == "PROPOSE_NDA_REVIEW":
        paras += ['<p>Please provide any proposed confidentiality undertaking or NDA for review.</p>']
    paras += ['<p>Please also confirm:</p><ul>']
    paras += [f'<li>{esc(question)}</li>' for question in data["qualificationQuestions"]]
    paras += ['</ul>',
              '<p>No financing method, finance pre-approval or purchasing entity is confirmed by this enquiry.</p>']
    if data["responseDueDate"] is not None:
        paras += [f'<p>Requested response date: {esc(data["responseDueDate"])}.</p>']
    paras += [f'<p>Kind regards,<br>{esc(data["sender"]["name"])}<br>{esc(data["sender"]["email"])}</p>']
    return '<div style="font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.45;color:#171A1F">' + "".join(paras) + "</div>"


def _native_validate(payload, family, component):
    if family == "BIAN":
        spec = yaml.safe_load((ROOT / "sources/bian/14.0.0/Correspondence.yaml").read_text())
        schema = {"$ref": "#/components/schemas/" + component, "components": spec["components"]}
    elif family == "TMF681":
        spec = _json(ROOT / "sources/tmforum/4.0.0/TMF681.swagger.json")
        schema = {"$ref": "#/definitions/" + component, "definitions": spec["definitions"]}
    else:
        raise ValueError("No licensed ACORD source or approved insurance profile installed")
    # Structural component validation only: this does not execute an API or certify conformance.
    Draft4Validator(schema, format_checker=FormatChecker()).validate(payload)


def prepare_preview(envelope):
    profile = _profile(envelope.get("schema", {}).get("id"), envelope.get("schema", {}).get("version"))
    verify_sources()
    _validate_local(envelope)
    if envelope["subject"]["objectId"] != envelope["data"]["reference"]:
        raise ValueError("Envelope subject and business reference disagree")
    data = envelope["data"]
    if data["profile"]["key"] != profile["key"] or data["profile"]["version"] != profile["version"]:
        raise ValueError("Business payload and selected profile disagree")
    content = render_message(data)
    recipients = data["to"] + data["cc"]
    # TMF receiver does not encode To/Cc roles in this source. Preserve those separately.
    tmf = {"messageType": "Email", "subject": data["subject"], "content": content,
           "sender": copy.deepcopy(data["sender"]), "receiver": copy.deepcopy(recipients)}
    bian = {
        "CorrespondenceSourceReference": envelope["eventId"],
        "CorrespondenceContent": content,
        "CorrespondenceAddressee": {"AddressDescription": "; ".join(p["email"] for p in data["to"])},
        "CorrespondenceMediaorChannel": {"ChannelType": "CommunicationChannel"},
        "CorrespondenceRecord": {"CorrespondenceContent": content,
                                 "CorrespondenceCommunicationMethod": "Email",
                                 "CorrespondenceMedium": "Electronic"}}
    response = {}
    if data["responseDueDate"] is not None:
        response["ResponseDueDate"] = {"DateTimeContent": data["responseDueDate"]}
    _native_validate(tmf, "TMF681", "CommunicationMessage_Create")
    _native_validate(bian, "BIAN", "Outbound")
    if response:
        _native_validate(response, "BIAN", "OutboundWithResponse")
    return {
        "status": "REVIEW_PREVIEW", "dispatchEnabled": False,
        "profile": {"key": profile["key"], "version": profile["version"],
                    "approvalStatus": profile["approvalStatus"]},
        "transport": {"to": copy.deepcopy(data["to"]), "cc": copy.deepcopy(data["cc"])},
        "tmf681": tmf, "bianOutbound": bian, "bianOutboundWithResponse": response,
        "correlationId": envelope["correlationId"], "idempotencyKey": envelope["idempotencyKey"],
        "limitations": [
            "Structural validation is not semantic approval or API conformance certification.",
            "To/Cc roles remain in transport metadata; projections are not lossless or reversible.",
            "No response match, sent status, delivery receipt or production authority is inferred.",
            "Free-text facts and financial disclosures require source and confidentiality review.",
            "No production adapter or dispatch function is implemented."]}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate and preview a candidate message; never send.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare_preview(_json(args.input)), indent=2))
