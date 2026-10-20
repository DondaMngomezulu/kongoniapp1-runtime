# Universal governed outbound message release gate (review candidate)

**Status:** ENGINEERING CANDIDATE / NOT DEPLOYED / NOT AUTHORISED FOR SEND. **Issue:** [#67](https://github.com/DondaMngomezulu/kongoniapp1-runtime/issues/67). Parent [ADR-HUB-FOUNDATION-001](../architecture/ADR-HUB-FOUNDATION-001.md).

The authoritative business schema register remains [ROR-0095 — Enterprise Message Schema Register](https://docs.google.com/spreadsheets/d/1TlHa9Q43Y-xJr-QJN4QveO0TKhT9hwm13K0wpX6BGVI/edit), controlled draft; [REG-STD-001](https://docs.google.com/spreadsheets/d/1tA7rKtgwkw57uROBC1Cht4rlOEjuQ60bLnhA-Daen6M/edit) controls standards and [REG-KNG-BDT-001](https://docs.google.com/spreadsheets/d/1OxgfobMF19ZrWg6pLuuhG_ZZNiTVUtcQgdEdSXEXw78/edit) controls business document type bindings. Existing [MRG-CVR-001](https://docs.google.com/document/d/13gOyII96BswC7z5SioCfE7YAjjyE3KyWDRGJO5AwmTk/edit) covering-email merge controls are inherited. No parallel register is introduced.

## Applicability matrix

| Family | Applicability | Structural artifact must be explicit |
| --- | --- | --- |
| OASIS | UBL commercial payloads (adopted 2.5); LegalDocML/LegalRuleML only when document/rule scope fits; ebMS/AS4 only after separate applicability/adoption | Normative XSD for the exact business document and edition; transport may be separate |
| ACORD | Insurance policy, coverage, premium, claims and insurance transactions | Licensed edition/transaction message XSD or other published contract, exact profile approval |
| BIAN | Financial service domain and business scenarios; service operations only where defined | Exact approved Semantic API/OpenAPI or local governed payload schema; **service-domain name is NOT itself a message schema** |
| TM Forum | Customer communications (TMF681), party interaction (TMF683), sales/order and other applicable APIs | Exact Open API/JSON Schema artifact, version and approved enterprise adaptation |

## Release contract

For every outbound governed message, require: business message type, matched approved standard edition and exact artifact URI, approved registered profile/version, validated actual payload, reconciled source business record, resolved approved template/merge, verified issuer and counterparty, channel/rendering/provider binding, consent where applicable, authorisation/approval evidence, correlation/idempotency, immutable audit reference and provider interception/readback evidence.

`outbound_release_gate.py` checks schema and cross-field decision prerequisites; trusted profile/standard snapshots are passed separately. **It does not itself parse the normative XSD/OpenAPI, authenticate evidence, control provider sends, or implement CRM enforcement.** An `ALLOW_CANDIDATE_ONLY` result means synthetic-policy satisfaction and SHALL NEVER trigger delivery. The production interceptor must authenticate evidence, run actual normative validation, bind send adapters and implement the authorised policy.

## Fail-closed runtime design

1. Native CRM validation/Blueprint/Function where sufficient for `CustomerCommunications`; secure outbound outbox/gateway for email, mass mail, WhatsApp, agents and external adapters.
2. All provider calls, including direct `ZohoCRM_sendMail`, MUST consult the same validated release authority or be technically inaccessible except through it. No claim of universal control until bypass attempts fail in Development.
3. Rule failure: DENY with reason, correlation, evidence, owner and an internal remediation path. Do not permit user input or agent reasoning to self-certify checks.
4. No production change until complete profile approval, independent CI and real payload test, security review, approved ACT decision, CRM/Catalyst Development canary and production deployment readback.

## Run synthetic tests

```sh
python governance/message-schemas/tests/test_outbound_release_gate.py
```

Fixtures contain invented identities. Do not commit real customer records, bank accounts, secrets or production sending tokens.
