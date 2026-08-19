#!/usr/bin/env python3
"""Validate governed LegalRuleML artifacts against the official OASIS compact XSD.

The validator downloads the official schema dependency graph at execution time,
rewrites schemaLocation references to a local cache, and validates every .xml/.lrml
file in the governed target directory. No Kongoni substitute schema is used.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from lxml import etree

DEFAULT_SCHEMA = (
    "https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/v1.0/os/"
    "xsd-schema/compact/lrml-compact.xsd"
)
ALLOWED_HOSTS = {"docs.oasis-open.org", "www.w3.org"}
XS = "http://www.w3.org/2001/XMLSchema"


def download(url: str) -> bytes:
    host = urlparse(url).hostname
    if host not in ALLOWED_HOSTS:
        raise RuntimeError(f"Refusing schema dependency from unapproved host: {url}")
    req = Request(url, headers={"User-Agent": "Kongoni-LegalRuleML-Validator/1.0"})
    with urlopen(req, timeout=30) as response:
        return response.read()


def cache_schema(url: str, cache: Path, seen: dict[str, Path]) -> Path:
    if url in seen:
        return seen[url]

    suffix = Path(urlparse(url).path).suffix or ".xsd"
    local = cache / f"{hashlib.sha256(url.encode()).hexdigest()[:16]}{suffix}"
    seen[url] = local

    raw = download(url)
    doc = etree.fromstring(raw)
    for node in doc.xpath("//xs:import[@schemaLocation] | //xs:include[@schemaLocation]", namespaces={"xs": XS}):
        child_url = urljoin(url, node.get("schemaLocation"))
        child_path = cache_schema(child_url, cache, seen)
        node.set("schemaLocation", child_path.name)

    local.write_bytes(etree.tostring(doc, xml_declaration=True, encoding="UTF-8"))
    return local


def targets(root: Path) -> list[Path]:
    return sorted([p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".xml", ".lrml"}])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-dir", default="agent-workspace/legalruleml")
    parser.add_argument("--schema-url", default=DEFAULT_SCHEMA)
    args = parser.parse_args()

    target_dir = Path(args.target_dir)
    files = targets(target_dir) if target_dir.exists() else []
    if not files:
        print(f"BLOCKED: no governed LegalRuleML targets found under {target_dir}")
        return 2

    with tempfile.TemporaryDirectory(prefix="kongoni-lrml-xsd-") as tmp:
        cache = Path(tmp)
        schema_path = cache_schema(args.schema_url, cache, {})
        schema = etree.XMLSchema(etree.parse(str(schema_path)))

        failures = 0
        for path in files:
            try:
                doc = etree.parse(str(path))
            except etree.XMLSyntaxError as exc:
                failures += 1
                print(f"FAIL {path}: XML not well formed: {exc}")
                continue

            if schema.validate(doc):
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                print(f"PASS {path} sha256={digest}")
            else:
                failures += 1
                print(f"FAIL {path}: OASIS compact XSD conformance errors")
                for err in schema.error_log:
                    print(f"  line={err.line} column={err.column}: {err.message}")

        if failures:
            print(f"LegalRuleML XSD conformance FAIL: {failures}/{len(files)} target(s) failed")
            return 1

        print(f"LegalRuleML XSD conformance PASS: {len(files)} target(s)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
