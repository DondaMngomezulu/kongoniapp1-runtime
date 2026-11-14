# Enterprise Concern and Object Completeness Profile — DRAFT
Status: **ENGINEERING PROPOSAL / NOT APPROVED OR DEPLOYED**. Tracks [#59](https://github.com/DondaMngomezulu/kongoniapp1-runtime/issues/59).

## Authority, source and precedence
- TOGAF method: [KEA-TA-001 v1.1](https://docs.google.com/document/d/1RQ3eQgjIqK3YJXEC-5r_OMhlw4FtiBIwDKi_ZeXiDwc/edit).
- Approved EA baseline: [KEA-MOD-EA-001 v1.9](https://docs.google.com/document/d/1lUSPGEsKW99pMQwvByjZtAWTN2n48Fw5n-0Pc22YMj8/edit).
- Approved governing concerns: [EA-GOV-LND-001 v1.0](https://docs.google.com/document/d/19H9mYRn2xq8086njP6xHLOqyf7QQ7SkPrNjvqpcChvw/edit).
- Approved metamodel/view catalogue: [KEA-SCH-REP-001](https://docs.google.com/spreadsheets/d/1rx-Hq1GDlbqiXA3R0xtwwaqb1eZklPyVwx-qHWU0YrU/edit).
- Standards register: [REG-STD-001](https://docs.google.com/spreadsheets/d/1tA7rKtgw57uROBC1Cht4rlOEjuQ60bLnhA-Daen6M/edit), ArchiMate Specification **3.2**, TOGAF **10**.
- Hub authority: [ADR-HUB-FOUNDATION-001](../ADR-HUB-FOUNDATION-001.md).
- Three-layer/seven-dimension [corrigendum](https://docs.google.com/document/d/1_x3sq6a51FOOk7UeJZveg86mPBqPVHeEleufbUovoJA/edit) is **WORKING / PRE-CONTROLLED**: project its proposed axes as candidate mappings only, not as a replacement for the approved five-domain view.
- Existing authority bindings `MAT-INFO-REPO-AUTH-001`, `CTL-DATA-REPO-ROUTE-001`, `REG-REPO-BINDING-001` are referenced by the hub standard; their current records and approval must be inspected before registration or changes.
- No public/customer-specific transaction instances, CRM exports, secrets, email bodies or business evidence in GitHub.

## 1. Sufficient concern specification
A governance **area** is not itself proof that every stakeholder **concern** has been captured. Retain all 12 approved areas: GOV-01 Corporate Governance and Direction; GOV-02 Enterprise Architecture Governance; GOV-03 Policy, Risk, Legal, Regulatory and Compliance Governance; GOV-04 Security and Privacy Governance; GOV-05 Data and Information Governance; GOV-06 API, Integration and Interoperability Governance; GOV-07 AI, Analytics and Automation Governance; GOV-08 Knowledge, Document and Records Governance; GOV-09 Transformation, Investment, Portfolio and Change Governance; GOV-10 Performance, Metrics and Maturity Governance; GOV-11 Resilience, Continuity and Operational Assurance; GOV-12 Sourcing, Supplier, Cloud and Responsible-Technology Governance.

For **each concern**, require:
1. Existing concern ID or PENDING allocation, label, definition, bounded applicability, priority, source and provenance.
2. Concerned stakeholder/role, driver, interest and desired measurable outcome.
3. Governance area, canonical single primary domain-view ID, affected value streams, legal entities, partners and boundaries.
4. Governing policy/principle, obligation, risk, control objective and source authority/version.
5. Requirements with testable acceptance criteria, thresholds and exception authority.
6. Affected business capabilities/services/processes; information objects and authoritative sources; application components/services/APIs; technology nodes/services.
7. Baseline finding, target expectation, approved transition, related gap, architecture/solution building blocks and work package.
8. Control implementation, evidence link, owner, reviewer, last review, lifecycle, conformance, approval and time-bounded exceptions.
9. Trace links MUST resolve to existing canonical object IDs rather than duplicate concern-specific object definitions. An unverified relationship is PENDING with an explicit hold, **never silently accepted**.

Reference EA-GOV-LND-001 minimum governed artifacts: GOV-DIR-001, GOV-PRN-001, GOV-OBL-001, GOV-DEC-001, GOV-RSK-001, GOV-CTL-001, GOV-ARC-001, GOV-SEC-001, GOV-DAT-001, GOV-API-001, GOV-AI-001, GOV-KRM-001, GOV-TRN-001, GOV-MET-001, GOV-RES-001, GOV-SRC-001, GOV-STD-001, GOV-ASR-001, GOV-XMAP-001, GOV-BT-001, GOV-RDM-001. The source approves artifact **definitions**, not automatic completion/publication of each artifact.

## 2. Sufficient object specification
For each **architecture object**, collect (or mark OPEN):
- **Identity**: immutable canonical ID, external reference(s), type, preferred name, precise meaning/inclusions/exclusions, business owner, custodian, canonical registry location and evidence.
- **Classification**: ONE primary Domain View EA-DV-01..05, independent supporting hierarchy EA-HV-H0..H4, strategic/segment/capability/solution/implementation detail, architectural state Baseline/Transition/Target, effective/observation dates, lifecycle/status, value stream, legal entity, stakeholder, confidentiality, retention.
- **Semantics**: concept/designation/classification/specification/property/value/unit/configuration/relationship/provenance, approved dictionary/standard & pinned release, mappings to the 7 semantic dimensions only if justified; data types/cardinality/units/controlled code lists.
- **Behaviour**: responsibilities, provided/required services, pre-/postconditions, initiating events, state transitions, approvals, timing, outcomes, errors, compensation/retry/idempotency.
- **Information authority**: transaction/master/reference/ledger/document/evidence/runtime/configuration classification; authoritative application/repository; primary key, foreign ID bindings, lineage, synchronisation, retention, legal hold, conflict resolution.
- **Structure/dependencies**: allowed ArchiMate 3.2 relationship types, source/target validity, cardinalities, interfaces, constraints, dependencies, threats and control ownership.
- **Delivery**: baseline/target mapping, identified gaps, implementation building block, technology/runtime placement, financial/nonfunctional measures, work package, release, approved exception and acceptance evidence.

No object is COMPLETE if its mandatory source/owner/identity/authority/acceptance evidence is unresolved. A source register's global completion statistic cannot substitute for each individual object.

## 3. ArchiMate 3.2 element-type coverage inventory — candidate checklist
Model the actual enterprise using valid concrete types and valid relations. Coverage is a **disposition** for each concrete type (PRESENT / UNMODELLED_GAP / NOT_APPLICABLE_WITH_REASON), separately in Baseline and Target, **not** a requirement to invent one instance of every type.

- **Motivation (10)**: Stakeholder, Driver, Assessment, Goal, Outcome, Principle, Requirement, Constraint, Meaning, Value.
- **Strategy (4)**: Resource, Capability, CourseOfAction, ValueStream.
- **Business (13)**: BusinessActor, BusinessRole, BusinessCollaboration, BusinessInterface, BusinessProcess, BusinessFunction, BusinessInteraction, BusinessEvent, BusinessService, BusinessObject, Contract, Representation, Product.
- **Application (9)**: ApplicationComponent, ApplicationCollaboration, ApplicationInterface, ApplicationFunction, ApplicationInteraction, ApplicationProcess, ApplicationEvent, ApplicationService, DataObject.
- **Technology (13)**: Node, Device, SystemSoftware, TechnologyCollaboration, TechnologyInterface, Path, CommunicationNetwork, TechnologyFunction, TechnologyProcess, TechnologyInteraction, TechnologyEvent, TechnologyService, Artifact.
- **Physical (4)**: Equipment, Facility, DistributionNetwork, Material.
- **Implementation & Migration (5)**: WorkPackage, Deliverable, ImplementationEvent, Plateau, Gap.
- **Other and connectors (4 candidates)**: Location, Grouping, AndJunction, OrJunction. Junctions are **relationship connectors**, not domain business objects; count separately from actual elements.
- **Relationships (11)**: Composition, Aggregation, Assignment, Realization, Serving, Access, Influence, Association, Triggering, Flow, Specialization.
- **Properties/notations**: Access type read/write/read-write; influence sign where relevant; directedness, nesting, junction usage, relationships-to-relationships and specializations must respect the adopted ArchiMate 3.2 language/exchange profile. This inventory is an **engineering starting list**, NOT independently verified exact language metamodel/exchange-schema completeness; validate against the official pinned specification and normative exchange XSD before a 100% conformance claim.
- **Views**: stakeholder and concern, domain, capability, value stream, process, information authority, application cooperation, integration, runtime/technology, security, AI/agent authority, implementation/migration, physical/asset, cross-value-stream, baseline/target and traceability.
- **Whole-enterprise coverage**: model all source-approved value streams, legal entities, external actors and partnerships; record omissions as gaps, not exclusions by default.

## 4. Candidate transaction and repository boundaries
Business transaction identity, state, accountable approvals and interaction history -> **Zoho CRM**. Governed documents, supporting source files and non-transactional document history -> **Google Drive** with CRM reference. Design/schema/code/configuration and synthetic fixtures -> **GitHub**. Integration execution/ephemeral state, observability and technical receipts -> **Catalyst**. Statutory accounting and other approved specialist operational systems retain their legally/operationally required native entries; CRM tracks linked business transaction and status, not a duplicated journal. Existing hub-authoritative-spoke policy takes precedence. Do not promote a blanket 'all stored records in CRM' rule over specialist ledgers and approved governed registers.

## 5. Conformance algorithm and release gates
1. Reconcile each canonical source register and its version; deduplicate aliases; identify missing population and approval state.
2. Build the concern-to-object matrix and object-to-authority matrix for **Baseline**, **Transition**, **Target**.
3. Verify each domain/concern/object definition, stakeholder linkage, value stream, valid semantic and ArchiMate relationships, reference source, canonical identity, ownership and exception.
4. Produce machine-readable ArchiMate Exchange XML; run schema + relationship-legality check; compare element count/type matrix for both states and trace links to actual model objects.
5. Negative cases: orphan concern; ownerless object; untyped object; duplicate canonical ID; more than one active primary Domain View; unresolved authority; wrong cross-domain master; invalid relation endpoints; missing baseline-target correspondence; open gap without work package; approval missing; document body/customer transactions in GitHub.
6. Record **counts and denominators**: governed concern areas; stakeholder concerns; governed architecture objects; modelled objects by type; justified non-applicable types; requirements; complete trace paths; source/CRM/runtime readback evidence.
7. Release only if all mandatory objects and concerns are either verified COMPLETE or registered GAP with accountable owner and approved, expiry-bound waiver where needed. Coverage-model syntax success is **not** full enterprise coverage.
8. Before production, independent review, required CI, development readback, explicit PDCA CHECK/STUDY and CEO ACT, plus CRM operational remediation actions.

## Observed gaps as at 2026-10-10
- Approved EA landscape explicitly lists Data, Application and Technology domain landscapes as requiring codification.
- Working three-layer/seven-dimension corrigendum is not a published revision.
- Existing repository Architecture_Content_Metamodel lists important Business/Domain View rules, but is **not itself** a demonstrated complete ArchiMate 3.2 instance inventory.
- CRM message-schema template/runtime enforcement remains OPEN, linked to [#57](https://github.com/DondaMngomezulu/kongoniapp1-runtime/issues/57).
- Complete concern-to-object/requirements-to-control crosswalk and independently conformance-tested Baseline/Target ArchiMate models are not yet evidenced.
- **Therefore global 'all concerns and objects are complete' claim is BLOCKED.**
