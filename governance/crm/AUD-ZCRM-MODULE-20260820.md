# AUD-ZCRM-MODULE-20260820 — Zoho CRM Module Architecture Audit

## Status
CHECK/STUDY complete against latest governed live-module snapshot. Fresh 2026-08-20 tenant read-back was unavailable because the Zoho CRM connector was unavailable in-session.

## Authority and method
- Governing methodology: MET-PDCA-001
- Generic semantic anchor: TM Forum SID Business Entity / persistent identity principles
- Financial-services refinement: BIAN Control Record
- CRM engineering rule: BR-ZCRM-ENG-001 as stress-tested with authoritative-spoke criterion
- Source evidence: AUD-ZCRM-RAT-001, live CRM module metadata read-back dated 2026-08-19

## Canonical module test
A CRM module is justified only where the represented object is a governed business entity or independently governed business record whose instances require persistent identity and independent lifecycle management, whose attributes or relationships justify separate persistence, and for which Zoho CRM is the designated authoritative spoke.

A semantic concept, status, classification, subtype, projection, workflow state, derived result, screen, or dependent detail is not sufficient by itself to justify a module.

## Audit dispositions

### KEEP — module is architecturally justified
- Agreements
- CustomerProducts
- ProductCatalogues
- ProductSpecifications
- ProductTaxonomy
- ProductArtifacts
- MachineModels
- EquipmentAssets
- ServiceSpecifications
- PartyRelationships

### CONVERT — current module should become attribute/view/projection
- AvailableProducts -> governed view/projection
- CustomerFinanceStatuses -> governed status attribute on owning entity
- CustomerInsuranceStatuses -> governed status attribute on owning entity
- CustomerContractMiningStatuses -> governed status attribute on owning entity
- CustomerOverviews -> view/dashboard/widget/projection
- AvailableCustomerServices -> governed view/projection

### MERGE / SPECIALISE — duplicate or subtype module
- CustomerAgreements -> merge into Agreements or retain only as a true relationship entity if independent attributes/lifecycle exist
- MARC_Contract -> Agreement subtype unless independent lifecycle/schema test passes
- Windscreen_claim -> Claims subtype unless independent lifecycle/schema test passes
- Deals_X_Contacts2 -> merge into one canonical Deal-Contact relationship structure
- Price_Books_X_Products2 -> merge into one canonical Price Book-Product relationship structure

### CONDITIONAL — requires field/record/lifecycle/dependency proof
- CustomerServices
- ProductQualifications
- ServiceEntitlements
- PartyRoles

## Semantic findings
1. Ontology concepts and CRM modules are not equivalent. The ontology defines meaning; CRM modules are physical persistence choices.
2. Subtypes should normally be represented through type, layout, controlled fields and lifecycle configuration rather than separate modules.
3. Status concepts belong to their owning entity unless there is an independently governed status-event ledger.
4. Relationship modules are justified only when the relationship itself has attributes, effective dates, provenance, lifecycle or governance.

## Architectural findings
1. CRM should remain the authoritative spoke for customer/party/commercial persistent state, not the enterprise semantic repository.
2. Signed/controlled documents remain outside CRM content authority; CRM holds references and commercial lifecycle metadata.
3. Accounting state belongs to the accounting spoke; telemetry and engineering artifacts belong to their designated spokes.
4. Module design must therefore apply both the entity test and the authoritative-spoke test.

## Risk assessment
- Current configuration has clear module proliferation from statuses, projections and subtypes.
- Immediate destructive rationalisation is not authorised because dependencies, record populations, layouts, Blueprints, workflows, views, APIs and integrations require regression testing.
- Retaining the current state indefinitely creates duplicate authority, semantic drift and increased configuration complexity.

## Recommendation
ACT recommendation: ADAPT.

Create and adopt a Target-State CRM Module Catalogue with three gates before implementation:
1. Fresh live tenant module/field/record inventory.
2. Dependency and lifecycle regression for every MERGE, CONVERT and CONDITIONAL object.
3. Migration plan with read-back evidence before retiring any current module.

Target principle: fewer durable modules, richer governed relationships/attributes/views, and explicit spoke authority.

## Freshness limitation
This audit uses the latest governed live CRM metadata snapshot captured 2026-08-19. A fresh read-back on 2026-08-20 is mandatory before executing configuration changes.
