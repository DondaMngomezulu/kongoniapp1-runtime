# Enterprise Writing Framework — candidate schema profiles

Status: **REVIEW DRAFT / NOT ADOPTED**. This package is architecture-as-code, not a transactional record store.

## Purpose
A shared JSON Schema Draft 2020-12 document envelope plus **18 separate discipline-specific JSON schemas**, with one unique profile per discipline. The required discriminators, required specialist fields and validation cases prevent accidental cross-discipline representation. All candidate URNs are explicitly provisional.

## Authority and precedence
- The controlled Enterprise Reference Standards Register **REG-STD-001** and Business Document Type Register **REG-KNG-BDT-001** remain in Google Drive. GitHub does not replace their approval authority or serve as a store for live CRM records.
- Native normative schemas for each document type (including OASIS UBL 2.4 quotation and invoice profiles recorded in REG-BDT-018) supersede the generic writing-envelope structure for their native transaction payloads.
- Most suggested published standards address only a subset of a writing discipline. This package **does not** claim full external-native schema conformance; subset gaps remain open.
- JSON Schema Draft 2020-12 provides the enterprise JSON format. External XML, XMI, RDF and linked-data formats retain their published validators and structural rules.
- The status fields `native_conformance: NOT_TESTED` and `semantic_alignment: NOT_VERIFIED` must not be overridden by ordinary JSON Schema passing.
- FIBO/BIAN semantic-hold decisions and applicable entity/period accounting-framework decisions remain open unless independently resolved.

## Contents and tests
- `manifest/discipline-profile-mapping.json` — proposed discipline-to-primary-profile map.
- `schemas/common/document-envelope.schema.json` — versioned common structural envelope.
- `schemas/profiles/*.schema.json` — 18 unique specialist JSON profile schemas.
- `tests/test_profiles.py` — sample generation, positive and negative structural validation.
- `requirements-test.txt` — test dependencies.

Run locally:
```sh
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
```

## Release gates
Source/version verification -> concept equivalence and identifier approval -> document-type native structural validation -> enterprise JSON schema validation -> business rules/Schematron/SHACL where applicable -> CRM template/field binding regression -> human approval -> controlled deployment. External-native conformance, legal enforceability and regulatory acceptance are not established by this package. Do not promote this branch or approve a standard based solely on these structural tests.
