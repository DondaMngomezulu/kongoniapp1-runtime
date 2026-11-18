# ADR-COMP-AGR-001 — Enterprise Computable Agreement Architecture

- **Status:** PROPOSED_FOR_REVIEW (not adopted, not deployed)
- **Version:** 0.1
- **Date:** 2026-10-09
- **Scope:** Enterprise-wide, for each agreement that passes the applicability assessment
- **Parent architecture:** `STD-ARCH-HUB-SPOKE-001`, `ADR-HUB-FOUNDATION-001`, `KEA-MOD-HS-001`
- **Method:** `MET-PDCA-001`
- **Machine-readable target profile:** `agent-workspace/reference-artifacts/legal/PRF-AGR-COMPUTABLE-001.yaml`

## Decision proposed

Maintain a strict separation between **(1) the authoritative executed agreement**, **(2) its
structured legal text and semantic representation**, **(3) machine-represented obligations,
permissions and prohibitions**, **(4) contractual financial calculations**, **(5) typed
executable decisions**, **(6) authorised external actions**, and **(7) independently auditable
actual events**. Each layer must refer to stable agreement, clause, rule, model and event
identifiers, versions and source hashes.

This architecture extends—not replaces—`CAT-SA-AGR-PREC-001`, `REG-AGR-TPL-001`,
`PRF-AGR-CLAUSE-PKG-001`, `PRF-AGR-TPL-VAL-001`, `CTL-LEGALRULEML-XSD-001`,
`REG-STD-001` and the enterprise concept dictionary.

**A computational execution is not execution of the legal instrument.**
Machine-generated representations, cash-flow schedules, notices, model parameters or
decisions must never themselves vary, discharge, novate, cede or replace signed instruments.

## Architecture layers and normative roles

| Layer | Authoritative function | Standards / implementation references | Important limit |
| --- | --- | --- | --- |
| L0 Signed legal record | Governing executed instrument, signatures, amendments, original terms, historic legally effective events | Approved matter repository; records governance | Source must be verified; GitHub is not the executed-document master |
| L1 Structured legal document | Stable clause anchors, cross-references and metadata | OASIS LegalDocML/Akoma Ntoso 1.0 **only where contract schema coverage is established**; otherwise a governed XML/document profile | Akoma Ntoso's stated primary coverage is parliamentary, legislative and judicial documents; do not claim every private agreement is natively conformant |
| L2 Canonical semantics | Jurisdiction-appropriate concepts, agreement class, actor roles, governed fields, provenance | South African law; enterprise concept dictionary; ISO/IEC 11179; OASIS RegRep; FIBO as reviewed overlay | No inferred FIBO equivalence or newly invented governed URI |
| L3 Normative rules | Legal obligations, rights, permissions, prohibitions, conditions, defeasibility and applicability | OASIS LegalRuleML Core 1.0 and `CTL-LEGALRULEML-XSD-001` | XML validity does not prove legal interpretation or runnable semantics |
| L4 Financial events | Interest, repayments, schedules, contractual financial event projections | ACTUS technical specification + pinned dictionary/engine for **supported** instrument types | An ACTUS PAM loan cannot by itself implement equity conversion, legal consent or share issuance |
| L5 Executable decision logic | Typed deterministic computations and bounded policy decisions | Accord Project Concerto/Cicero patterns **ADAPT**; selected runtime with tests; DMN optional and presently PROPOSED in `REG-STD-001` | No Accord clause text is authoritative South African legal wording; LegalRuleML is not itself an approved execution engine |
| L6 Controlled action orchestration | Human-authorised signing, issuance, payments, notices and ledger writes through system-of-record gateways | Hub policy decision, MCP/OpenAPI/CloudEvents where applicable, identity, least privilege, audit controls | AI inference and simulation may not initiate a legally effective action without required authority |
| L7 Actual event and evidence | Source bank/Books transactions, validated notices, approvals, valuations, signed election evidence and receipts | Existing source systems, append-only provenance and `MET-PDCA-001` | Forecasts are not actuals; accounting records do not silently change contract rights |

## Enterprise applicability

Assess every agreement by its **legal instrument class** and the nature of its obligations.
Use an explicit `APPLICABLE`, `PARTIAL`, `NOT_APPLICABLE` or `BLOCKED` result with rationale,
source and reviewer. Do not mandate ACTUS for non-financial contracts.

- **Loans, credit facilities, instalment sales and finance leases:** use ACTUS only for the
  independently supported contractual financial component; legal rights remain in L0-L3.
- **Convertible loans and option-linked finance:** retain the principal model separately
  from conversion-option, valuation, election, consent and securities-issue logic; never
  infer conversion from a maturity date.
- **Operating leases, plant hire, rentals, sales, supply and services:** use structured
  legal text and legal rules when obligations can be represented; use typed logic for
  pricing, usage, acceptance or SLA tests where justified; use ACTUS only if an ACTUS
  supported financial instrument exists.
- **Guarantees, cessions, novations, amendments, waivers and terminations:** capture the
  specific signed instrument and its parties/effective date, then determine financial
  effect; do not infer a transfer or release from accounting mappings.
- **Non-deterministic, legal-judgment-only or purely narrative terms:** capture source,
  applicability, exception and manual-review outcome. Do not falsely label executable.

## Authority, ownership and service boundaries

- **Authoritative contract:** current approved repository and signed-document chain
  remain master; WorkDrive is a conditional migration target, not a silent replacement.
- **GitHub:** architecture, models, rule-engine code, tests, schema profiles and build
  provenance only; no customer contracts, privileged advice, credentials or live debt data
  in this public repository.
- **Zoho Catalyst / logical Hub:** policy-controlled orchestration, execution-state
  evidence and governed integrations. The logical Hub is not one vendor product.
- **Zoho CRM:** customer relationship, deal and commercial record state; it is not the
  legal signature or financial general-ledger source.
- **Zoho Books:** accounting ledger, actual postings and reconciliations; ACTUS forecast
  and historical calculations are projections until reconciled and authorised.
- **Existing services:** bind to `MS-VS00-DOCUMENT-SERVICES-001` for document integration
  and `MS-VS02-LEGAL-COMPLIANCE-001` for the VS02 legal-compliance use case; adapt
  boundaries through the governed Microservice Register. Reuse agreement computability
  capabilities across value streams without declaring a new overlapping service by default.

## Contract identity and events

A derivative `ComputableAgreementManifest` must include:
`agreement_id`, `agreement_class_id`, `source_uri`, `source_hash`,
`source_lifecycle`, `governing_law`, `party_role_refs`, `effective_date`,
`source_clause_refs`, `amendment_chain`, `model_version_refs`,
`rule_versions`, `financial_model_refs`, `actual_event_evidence_refs`,
`authority_decisions`, `interpretation_gaps`, and `promotion_state`.
Absent material source facts are null/blocked, never silently imputed.

Each event distinguishes `contractual_due`, `computed_forecast`,
`actual_evidenced`, `decision_proposed`, `authorised` and
`legally_effective`. Preserve as-of dates and revision lineage. Replaying history
does not rewrite the original dates or retrospectively sign an instrument.

## Mandatory prohibitions

- No change to source agreement, conversion rights, debt amount, parties, maturity,
  default protections or governing law caused solely by a model or data migration.
- No merging separate agreements, debt cession, debtor substitution, set-off, novation,
  release, waiver or cancellation without a specific effective source instrument and
  authority evidence.
- No inference of a legally binding option exercise, valuation, election, notice,
  share issuance, court remedy, funds transfer or accounting posting from a calculation.
- No model or AI-generated text promoted to `APPROVED` or `EXECUTED` because
  a JSON/YAML/XML validation test passed.
- No disclosure of matter data to public repositories, prompts, agents or external
  systems without permission and least-privilege controls.

## Architecture handover and conformance

Use `PRF-AGR-COMPUTABLE-001` and `PRF-ARCH-MICROSVC-HO-001`.
Require legal-source verification, rights-preserving clause-to-rule crosswalk,
schema/XSD validation when applicable, legal interpretation sign-off, independent
financial replay where applicable, synthetic tests, negative tests, security tests,
system-of-record reconciliation and PDCA evidence before production effect.

**Canary:** an unamended historical convertible loan must preserve its original
borrower, maturity and option terms; its ACTUS debt projection must not mark
conversion as having occurred without separately verified legally effective evidence.
Use synthetic identifiers and amounts in repository tests.

## Decision and implementation state

Architecture proposal and control definition only. ACT adoption/version, exact
LegalDocML schema coverage for private agreements, executable LegalRuleML
translation, accord runtime selection, DMN adoption, legal sign-off, financial
reconciliation and production gateway permissions are unresolved gates. No
microservice, contract or transaction is automatically built, approved or deployed
by this ADR.

## Reference baselines

- ACTUS: https://www.actusfrf.org/techspecs
- ACTUS dictionary: https://github.com/actusfrf/actus-dictionary
- OASIS LegalRuleML Core 1.0: https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/v1.0/os/legalruleml-core-spec-v1.0-os.html
- OASIS Akoma Ntoso 1.0: https://www.oasis-open.org/standard/akn-v1-0/
- Accord Project: https://docs.accordproject.org/docs/accordproject/
- Governed enterprise standards register: https://docs.google.com/spreadsheets/d/1tA7rKtgwkw57uROBC1Cht4rlOEjuQ60bLnhA-Daen6M/edit
