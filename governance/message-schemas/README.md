# Enterprise Message Schema Inventory — controlled draft v0.1

**Date:** 2026-10-09. **Governance state:** CONTROLLED DRAFT, NOT APPROVED. **Canonical register ID:** pending allocation through REG-REG-001. This is a subordinate engineering reference, not a second source of approval.

## Live source of truth

- [Working cross-domain inventory](https://docs.google.com/spreadsheets/d/1TlHa9Q43Y-xJr-QJN4QveO0TKhT9hwm13K0wpX6BGVI/edit) — 96 adopted source records, 5 implementation bindings, 14 standards, 4 GitHub engineering records, 10 open gates.
- [REG-KNG-BDT-001 document register](https://docs.google.com/spreadsheets/d/1OxgfobMF19ZrWg6pLuuhG_ZZNiTVUtcQgdEdSXEXw78/edit) — authority for `BDT-L1-UBL-001..093`, `BDT-L2-ENT-001..002`, and `SB-0001/0002/0003/0004/0006`.
- [REG-STD-001 reference standards](https://docs.google.com/spreadsheets/d/1tA7rKtgwkw57uROBC1Cht4rlOEjuQ60bLnhA-Daen6M/edit) — source standard adoption authority.
- [REG-REG-001 registry of registers](https://docs.google.com/spreadsheets/d/1AQm80yW-BAqaT5j2HYniNuJrwgH_FeBFaVqDdIm4rbk/edit) — approval/ID/lifecycle control.
- [MRG-CVR-001 CEO-adopted covering email merge schema](https://docs.google.com/document/d/13gOyII96BswC7z5SioCfE7YAjjyE3KyWDRGJO5AwmTk/edit) — approved 2026-10-09 under GOV-APR-10; associated child email templates require independent publication.

## Contract layers

1. **Business payload:** 93 source-adopted OASIS UBL 2.4 normative maindoc XSDs, plus 2 enterprise message/report profiles; one covering email merge schema.
2. **Transaction binding:** 5 currently evidenced `SB-*` bindings over UBL 2.4 (not proof of deployed conformance).
3. **Schema grammar:** XSD 1.1 and JSON Schema Draft 2020-12 adopted; language adoption never makes an individual payload production-approved.
4. **Finance/CRM semantics:** ISO 20022 and TM Forum SID frameworks adopted, exact message IDs, bank profiles, TMF683 crosswalk and Catalina binding pending. FpML 5.13 is an interoperability reference subject to instrument fit.
5. **Transport/event delivery:** MQTT adopted where applicable; AMQP/AS4 registered for applicability assessment, **not adopted**. Vendor-neutral canonical message/event envelope appears in [ADR-HUB-FOUNDATION-001](../architecture/ADR-HUB-FOUNDATION-001.md), but implementation and runtime verification are pending.
6. **Existing code contracts:** [agent-work-item](../../agent-workspace/schemas/work-item.schema.json), [handoff](../../agent-workspace/schemas/handoff.schema.json), [system-write-audit-event](../../agent-workspace/schemas/system-write-audit-event.schema.json), [TMF683 source index](../schemas/TMF683_PartyInteraction_v5.0.0.ingest.json). Code presence / indexed source provenance is not enterprise adoption or production evidence.

## Release gates

A schema is usable for production only when its governing source is adopted, a precise version and payload URI are bound, target process/application is confirmed, semantic and structural checks pass against representative payloads, and an authorised change/deployment approval plus independent readback exists. Keep these gates distinct.

**Open gates** (working IDs, not canonical IDs): MSG-GAP-01 register ID and authority; 02 UBL 2.4 vs 2.5; 03 ISO 20022 message-specific profiles; 04 UBL/CRM conformance; 05 event envelope and backbone; 06 TMF683/Catalyst; 07 covering email child templates; 08 FpML/ACTUS instrument fit; 09 Genericode status lists; 10 CI/deployment conformance.

Do not silently promote source-adopted rows or infer approval from this inventory; use a reviewed changeset, evidence and authorised REG-REG-001 approval before declaring this register canonical.
