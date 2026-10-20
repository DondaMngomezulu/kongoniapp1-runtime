# Reusable message profiles — review package v0.1
Date: 15 October 2026. Status: engineering candidate; not approved or deployed.

This extends the existing candidate canonical envelope for issue #53. It adds a version-selected information-request email profile, deterministic HTML renderer, pinned BIAN and TMF681 sources, native component projections, offline validation, synthetic examples and a proposed CI workflow. It creates no canonical enterprise identifier.

## Contracts and ownership
- The existing canonical-event-envelope schema is retained byte-for-byte.
- reusable-message-envelope adds required actor and idempotency metadata and binds the business payload by reference.
- information-request-email is an enterprise implementation schema, not a publisher-defined BIAN/TMF/ACORD message.
- profiles/registry.candidate.json selects exact versions; no implicit latest version.
- BIAN source: Correspondence 14.0.0, BOM/OpenAPI variant. Outbound contains message content; OutboundWithResponse contains only evidenced response metadata.
- TMF681 source: CommunicationMessage_Create 4.0.0, Swagger 2.0. To/Cc roles are preserved separately in transport metadata because this source Receiver object has no To/Cc role property.
- ACORD: STD-INS-ARCH-001 is adopted as reference architecture in REG-STD-001. Native insurance payload implementation is deferred until a relevant transaction family, licensed artifact, exact release, mapping and approval are evidenced. No placeholder schema is labelled ACORD.
- Unknown financing method, pre-approval and purchaser remain null in this initial-discovery profile. No source-bank details are part of the schema. Free-text statements still require factual/confidentiality review.
- Local profile keys, metadata and source manifests are not registered enterprise IDs or published normative schemas.

## Reuse
Install requirements.txt in a controlled environment, then invoke:
```bash
python governance/message-schemas/scripts/message_profiles.py INPUT.json
```
The callable prepare_preview(envelope) returns validated preview projections and dispatchEnabled=false. It does not send, deploy, create business records, grant authority or change the registry.

The same preview function can be invoked from an approved service or pipeline after engineering review. Native CRM controls and functions remain the first implementation choice for CRM enforcement and correspondence; this Python reference is not a mandated production hosting design.

## Validation
Run the existing envelope checks and the new profile tests:
```bash
python -m unittest discover -s governance/message-schemas/tests -p 'test_*.py' -v
```
Tests cover source corruption, required fields, timestamp/email formats, unknown versions, unsupported ACORD projection, BIAN enums, TMF mandatory fields, reference mismatches, HTML escaping, To/Cc retention, unknown financial facts and unverified authority assertions.

Structural validation of the selected source components does not prove semantic equivalence, official API certification, lossless conversion, customer consent, production authorisation or runtime integration. A preview is not a sent message. Idempotency metadata and deterministic previews do not implement durable duplicate-send prevention.

## Review and release
1. Confirm scope/version-specific mappings and the proposed initial-information wording.
2. Allocate canonical profile identifiers through existing governance if required.
3. Approve profile, mapping and renderer versions with independent evidence.
4. Resolve repository execution authority; publish a draft PR with the same-change-set log.
5. Execute GitHub CI and review the native-standard and CRM adapter boundaries.
6. Implement/test authorised channel dispatch, durable idempotency, delivery receipts and response matching separately.
7. Update the existing controlled message register after approval; do not create a parallel register.

Sources and status authority:
- REG-STD-001: https://docs.google.com/spreadsheets/d/1tA7rKtgwkw57uROBC1Cht4rlOEjuQ60bLnhA-Daen6M/edit
- Working message register: https://docs.google.com/spreadsheets/d/1TlHa9Q43Y-xJr-QJN4QveO0TKhT9hwm13K0wpX6BGVI/edit
- Existing envelope task: https://github.com/DondaMngomezulu/kongoniapp1-runtime/issues/53

The repository overlay contains synthetic fixtures only. Actual correspondence and deal examples belong in the separate private application folder of the review bundle, never in the GitHub overlay.

## Pre-adoption hardening — 15 October 2026
Adversarial testing found gaps in malformed-input handling, source-manifest coverage, metadata/source binding and message hygiene. The candidate now checks complete manifest coverage and publisher blob identity, rejects duplicate JSON members and unsupported native bindings, requires format-checker availability, validates bare mailbox syntax, preserves local-part case while comparing domains without case, rejects duplicate To/Cc recipients, header control characters, blank material text and unresolved template tokens.

The schema URI is bound to the selected profile. Its current urn:example reference is explicitly synthetic and remains a registration gate before production adoption. Registry metadata cannot enable dispatch in this preview implementation. Publisher signatures or trust in a package distribution are not established by hashes alone: the verifier and its source pins must be delivered through the reviewed repository/release.

These corrections tighten previously accepted candidate inputs without changing the pinned source standards or the 0.1.0 candidate key. No approved or production contract is migrated. Free-text factual accuracy, confidentiality and real-party authority still need review; this validator does not infer them.
