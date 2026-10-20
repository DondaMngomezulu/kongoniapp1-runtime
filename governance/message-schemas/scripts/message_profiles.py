"""Offline candidate message preparation. No network, dispatch or approval mutation."""
import copy
import hashlib
import html
import json
import re
from email.errors import HeaderParseError
from email.headerregistry import Address
from pathlib import Path

import yaml
from jsonschema import Draft4Validator, Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]

# Publisher Git blob identities form part of the reviewed verifier, separately
# from the editable manifest. They are not enterprise approval assertions.
NATIVE_RELEASES = {
    "BIAN": {"path": "sources/bian/14.0.0/Correspondence.yaml", "version": "14.0.0",
             "blobSha": "65c15ba330772a3b88af538d7bb5efb300b92bd7",
             "component": "Outbound"},
    "TMF681": {"path": "sources/tmforum/4.0.0/TMF681.swagger.json", "version": "4.0.0",
               "blobSha": "16f56e0ce2476cc5e3f756d5b9b98d11bb26a0af",
               "component": "CommunicationMessage_Create"}}
EXPECTED_SOURCE_PATHS = {release["path"] for release in NATIVE_RELEASES.values()} | {
    "sources/bian/LICENSE", "sources/tmforum/LICENSE"}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON member: " + key)
        result[key] = value
    return result


def _json(path):
    return json.loads(path.read_text(), object_pairs_hook=_unique_object)


def _profile(key, version):
    registry = _json(ROOT / "profiles/registry.candidate.json")
    if not isinstance(registry, dict) or not isinstance(registry.get("profiles"), list):
        raise ValueError("Malformed profile registry")
    if not all(isinstance(p, dict) and "key" in p and "version" in p for p in registry["profiles"]):
        raise ValueError("Malformed profile entry")
    matches = [p for p in registry["profiles"] if p["key"] == key and p["version"] == version]
    if len(matches) != 1:
        raise ValueError("Unknown or ambiguous profile/version")
    profile = matches[0]
    standards = profile.get("standards")
    if not isinstance(standards, list) or not all(isinstance(s, dict) for s in standards):
        raise ValueError("Malformed standard bindings")
    for family, release in NATIVE_RELEASES.items():
        bindings = [s for s in standards if s.get("family") == family]
        if len(bindings) != 1 or any(bindings[0].get(k) != release[k] for k in ("version", "component")):
            raise ValueError("Unsupported native binding: " + family)
        if bindings[0].get("source") != release["path"]:
            raise ValueError("Native source binding mismatch: " + family)
    return profile


def verify_sources():
    manifest = _json(ROOT / "sources/manifest.json")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
        raise ValueError("Malformed source manifest")
    entries = manifest["files"]
    if not all(isinstance(item, dict) and isinstance(item.get("path"), str) for item in entries):
        raise ValueError("Malformed source manifest entry")
    paths = [item["path"] for item in entries]
    if len(paths) != len(set(paths)) or set(paths) != EXPECTED_SOURCE_PATHS:
        raise ValueError("Source manifest must cover each pinned source and licence exactly once")
    for item in entries:
        path = (ROOT / item["path"]).resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise ValueError("Source path escapes package")
        if not path.is_file():
            raise ValueError("Pinned source missing: " + item["path"])
        contents = path.read_bytes()
        if hashlib.sha256(contents).hexdigest() != item.get("sha256"):
            raise ValueError("Pinned source digest mismatch: " + item["path"])
        for release in NATIVE_RELEASES.values():
            if item["path"] == release["path"]:
                blob = hashlib.sha1(b"blob " + str(len(contents)).encode() + b"\0" + contents).hexdigest()
                if item.get("version") != release["version"] or item.get("blobSha") != release["blobSha"] or blob != release["blobSha"]:
                    raise ValueError("Source differs from pinned publisher release: " + item["path"])


def _validate_local(envelope):
    if not {"date-time", "uuid", "uri", "email"}.issubset(FormatChecker.checkers):
        raise ValueError("Required format validators unavailable; install jsonschema[format]")
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


def _validate_message_text(data):
    def visit(value):
        if isinstance(value, dict):
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, str):
            if not value.strip():
                raise ValueError("Blank material message value")
            if "{{" in value or "}}" in value or "${" in value:
                raise ValueError("Unresolved template token")
            if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", value):
                raise ValueError("Control character in message text")
    visit(data)

    def header(value):
        if any(ord(char) < 32 or ord(char) == 127 for char in value):
            raise ValueError("Control character in header value")
    header(data["subject"])
    identities = set()
    for index, party in enumerate([data["sender"], *data["to"], *data["cc"]]):
        header(party["name"])
        header(party["email"])
        try:
            mailbox = Address(addr_spec=party["email"])
            if not mailbox.username or not mailbox.domain or mailbox.addr_spec != party["email"]:
                raise ValueError("Bare mailbox address required")
        except (ValueError, HeaderParseError, IndexError) as error:
            raise ValueError("Invalid bare mailbox address") from error
        # Preserve local-part case; DNS domain names are case-insensitive.
        identity = (mailbox.username, mailbox.domain.casefold())
        if index > 0:
            if identity in identities:
                raise ValueError("Duplicate recipient across To/Cc")
            identities.add(identity)


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
    _validate_local(envelope)
    profile = _profile(envelope["schema"]["id"], envelope["schema"]["version"])
    if envelope["schema"]["uri"] != profile.get("schemaUri"):
        raise ValueError("Schema reference and selected profile disagree")
    verify_sources()
    if envelope["subject"]["objectId"] != envelope["data"]["reference"]:
        raise ValueError("Envelope subject and business reference disagree")
    data = envelope["data"]
    _validate_message_text(data)
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
