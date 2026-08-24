---
name: tender-management-b2b-tmforum-oasis
governed_id: SKL-TND-MGMT-001
version: '1.2'
status: ADAPTED_FOR_REVIEW
owner: Chief of Accountability
business_domain: B2B tender, bid and proposal management
methodology: MET-PDCA-001
primary_reference_model: TM Forum ODA / eTOM B2B commercial lifecycle
normative_legal_reference_model: Kongoni-adopted OASIS LegalDocML / Akoma Ntoso + OASIS LegalRuleML profile
inherits:
  - BR-PDCA-001
references:
  - TMF699 Sales Management API / Lead and Opportunity Management TMFC036
  - TMF620 Product Catalog Management API
  - TMF679 Product Offering Qualification API
  - TMF648 Quote Management API
  - TMF651 Agreement Management API
  - TMF629 Customer Management API
  - TMF632 Party Management API
  - TMF669 Party Role Management API
  - TMF667 Document Management API
  - TMF683 Party Interaction Management API
  - TMF622 Product Ordering Management API
  - TMF668 Partnership Management API where partner participation applies
  - OASIS LegalDocML / Akoma Ntoso 1.0
  - OASIS LegalRuleML 1.0
  - W3C SKOS / RDF / JSON-LD / PROV-O where enterprise semantic/provenance bindings are required
  - Kongoni enterprise Product, Agreement, Counterparty, Value Stream, Task and Records governance
---

# Tender Management Skill — TM Forum B2B + OASIS Legal/Normative Process

## 1. Purpose

Use this skill to govern business-to-business tender, RFQ, RFP, EOI, bid and proposal work from discovery through award, agreement formation, order handoff, evidence-based review and controlled closure.

The skill SHALL treat Tender Management as a B2B commercial-process specialization aligned to TM Forum ODA/eTOM and applicable TM Forum Open APIs. It SHALL NOT create a competing enterprise sales lifecycle.

Kongoni SHALL use its enterprise-adopted OASIS LegalDocML/Akoma Ntoso representation profile for machine-readable legal/procurement document structure and stable governed fragment referencing. OASIS LegalRuleML SHALL provide the normative-rule semantics used for obligations, prohibitions, permissions, authority, overrides and compliance evidence.

A Tender is a Kongoni governed orchestration object for a customer procurement event and its evidence. It is not asserted to be a native TM Forum canonical resource. Its primary commercial anchor is the Sales Opportunity. Its legal and evidentiary anchors are governed Document, LegalDocumentFragment, LegalNorm and Agreement objects.

This skill defines the execution method and control requirements. Agent authority belongs in an Agent Contract. Deterministic transactional controls may be implemented through governed services or microservices, but those implementations SHALL conform to this skill.

## 2. Canonical object boundaries

The skill SHALL preserve the following distinctions.

### 2.1 Commercial objects — TM Forum-led

`SalesLead -> SalesOpportunity -> Tender -> TenderRequirement`

`ProductSpecification -> ProductOffering -> ProductOfferingPrice -> ProductOfferingQualification -> QuoteItem -> Quote`

`Quote -> Agreement -> ProductOrder -> Product`

Where a physical machine or other productive asset is involved, `Asset` remains a separate enterprise object linked to Product, Agreement and Order as applicable.

### 2.2 Legal and normative objects — OASIS-led

`LegalDocument -> LegalDocumentFragment -> LegalNorm`

`LegalNorm -> Obligation | Permission | Prohibition`

`LegalNorm -> Authority / LegalSource / ApplicabilityContext / Override`

`Obligation -> Bearer -> ComplianceEvidence`

The CRM Agreement record MAY be the transactional projection of an Agreement, but SHALL NOT be treated as the sole canonical legal-document or legal-rule representation.

### 2.3 Party-role separation

Commercial Party Roles and legal/normative roles SHALL NOT be collapsed into one vocabulary.

Commercial relationship example:

`Party -> PartyRole -> PartyRelationship`

Legal/normative example:

`Party -> LegalNormRole`, including roles such as Bearer or Authority where applicable.

The same Party may hold both commercial and normative roles in different contexts.

## 3. Canonical semantic mapping

The mandatory mapping is:

- external procurement notice / detected commercial interest -> TMF699 Sales Lead where qualification is not yet complete;
- qualified tender / RFQ / RFP pursuit -> TMF699 Sales Opportunity;
- procuring organisation -> TMF629 Customer and/or TMF632 Party, with TMF669 Party Role where role semantics are required;
- tender requirement -> Kongoni TenderRequirement linked to a source LegalDocumentFragment and, where applicable, ProductSpecification/ProductOffering and LegalNorm/Agreement obligation;
- offerable commercial proposition -> TMF620 Product Offering;
- underlying definition of what can be supplied -> Product Specification;
- commercial price of an offering -> governed ProductOfferingPrice / pricing record and pricing rule;
- feasibility / eligibility / technical fit -> TMF679 Product Offering Qualification or equivalent governed qualification result;
- authoritative customer quotation transaction -> TMF648 Quote where TMF648 is implemented;
- TMF699 Sales Quote semantics MAY represent the sales-management view/reference of the same quotation, but SHALL share identity or explicit cross-reference with TMF648 Quote and SHALL NOT create an independent commercial truth;
- contract framework / award instrument -> TMF651 Agreement / Agreement Specification;
- RFQ/RFP/addendum/submission evidence -> TMF667 Document plus enterprise controlled-record references;
- legal/procurement document internal structure and stable governed fragment identity -> Kongoni-adopted OASIS LegalDocML/Akoma Ntoso representation profile;
- contractual/policy obligations, permissions, prohibitions and overrides -> OASIS LegalRuleML;
- clarification, bidder communication and negotiation touchpoint -> TMF683 Party Interaction;
- successful award / executable demand -> TMF622 Product Order or governed downstream order/contract execution object;
- consortium, OEM, subcontractor or strategic partner involvement -> TMF668 Partnership plus Party / Party Role relationships as applicable.

The Tender object SHALL retain cross-references to canonical objects and SHALL NOT duplicate their authoritative state.

## 4. Tender lifecycle, gate status and decision separation

The canonical Tender lifecycle is:

`DISCOVERED -> QUALIFYING -> QUALIFIED -> BID_DECISION -> BID_IN_PREPARATION -> INTERNAL_REVIEW -> APPROVED_FOR_SUBMISSION -> SUBMITTED -> CLARIFICATION_NEGOTIATION`

Awarded path:

`AWARDED -> CONTRACTING -> ORDER_HANDOFF -> CHECK_STUDY -> ACT -> CLOSED`

Non-awarded terminal path:

`LOST | WITHDRAWN | CANCELLED -> CHECK_STUDY -> ACT -> CLOSED`

Lifecycle state, gate result and executive/operational decision SHALL be separate information objects or attributes.

`GateStatus = NOT_ASSESSED | PASS | HOLD | FAIL | EXCEPTION`

`BidDecision = BID | NO_BID | ESCALATE`

A work-status such as `DOCUMENTS_ACQUIRED` MAY exist as a Process_Substate but SHALL NOT replace canonical lifecycle state.

`Eligibility Hold` SHALL be represented as a qualification/gate outcome, not as a core lifecycle state.

`Bid Approved` SHALL be represented as a decision/approval result, not as a separate lifecycle state.

A tender may not advance to `QUALIFIED` until the customer/party, procurement event, due date, scope, value stream, target offering/product family and minimum eligibility evidence are identified.

A tender may not advance to `APPROVED_FOR_SUBMISSION` unless all required gates in this skill pass.

## 5. B2B tender process gates

### G1 — Lead / Opportunity qualification

Confirm:

- source and procurement-event identity;
- customer/party identity;
- buying organisation and relevant party roles;
- tender close date and submission channel;
- opportunity owner;
- target value stream and Product Specification/Product Offering family;
- commercial interest and strategic fit;
- mandatory eligibility criteria;
- bid/no-bid authority.

If the commercial interest is detected but not sufficiently qualified, keep it at Lead semantics. Once the buyer and pursuit are confirmed, promote to Sales Opportunity semantics.

### G2 — Requirement decomposition and source provenance

Parse the procurement pack into individually traceable requirements.

Every requirement SHALL have at minimum:

- `Requirement_ID`;
- `Tender_ID`;
- `Source_Document_ID`;
- stable governed `Source_Fragment_ID` where the source supports fragment identity;
- human-readable source clause/page locator where useful;
- requirement type;
- mandatory / scored / informational classification;
- response owner;
- compliance state;
- evidence reference;
- related ProductSpecification/ProductOffering where applicable;
- related ProductOfferingQualification where applicable;
- related LegalNorm / Agreement obligation where applicable.

Page number or free-text clause reference SHALL NOT be the only machine-readable provenance mechanism when fragment-level identity is available. Fragment immutability/version persistence is an enterprise records-governance requirement, not an OASIS claim.

Requirements SHALL be MECE at the level used for compliance checking.

### G3 — Product Specification, Product Offering and qualification

The skill SHALL NOT collapse Product Specification, Product Offering and realised Product into a single semantic object.

Every offered commercial line SHALL resolve through:

`ProductSpecification -> ProductOffering -> ProductOfferingQualification`

and to a governed CRM Product/ProductOffering representation used by the transactional system.

No free-text billable product may be introduced directly into a Quote.

If the required Product Specification, Product Offering or transactional Product does not exist, create or remediate the governed Product Master/catalogue before quotation approval.

### G4 — Governed pricing and Quote construction

TMF648 Quote SHALL be the authoritative customer quotation transaction where TMF648 is implemented. A TMF699 Sales Quote representation MAY be maintained as a sales-management projection/reference but SHALL cross-reference the authoritative Quote identity and version.

Every billable Quote Line SHALL reference:

- CRM Product / Product Offering transactional ID;
- canonical Product Offering or Product ID where required;
- Product Specification ID where applicable;
- quantity;
- usage unit;
- approved ProductOfferingPrice / pricing record;
- applicable pricing rule;
- currency;
- tax basis;
- effective date;
- applicable customer / programme / site / asset context;
- related Requirement_ID(s);
- authorised pricing override reference where an exception is permitted.

Draft Quotes MAY be incomplete while being assembled. Completeness becomes mandatory at controlled commercial states.

`BR-QUOTE-VALID-001:`

`Quote.status in {APPROVED, ISSUED, SUBMITTED, ACCEPTED} -> required_line_item_count = priced_required_line_item_count AND no required billable line is blank, TBC, unresolved or unpriced.`

`BR-QUOTE-LINE-SOURCE-001:`

`Every billable quotation line SHALL reference an active governed CRM Product/Product Offering and an approved CRM pricing source or formally authorised override.`

`BR-QUOTE-PRICE-PROVENANCE-001:`

`QuoteLine.Price SHALL resolve to an approved ProductOfferingPrice/PricingRule valid for the customer, programme, context and effective date, unless an authorised override is linked.`

Price Book or CRM list price is an implementation mechanism and SHALL NOT by itself be treated as the semantic parent or sole evidence of governed price.

### G5 — Agreement and legal-rule alignment

Before submission, map the offer to the applicable Agreement Specification and transaction-specific Agreement fields.

For operating lease / equipment rental pursuits, validate at minimum:

- fixed rental / availability charge;
- variable usage charge;
- included usage;
- escalation;
- term;
- asset identity requirements;
- maintenance/service separation or approved bundling;
- insurance;
- permitted use/site;
- acceptance;
- telemetry/meter source;
- residual/end-of-term treatment;
- legal/tax/accounting classifications where required.

The Quote SHALL NOT contain economics or obligations that cannot be represented in the approved Agreement and Product Specification model.

Each material contractual obligation SHALL resolve, where applicable, to:

- `LegalNorm_ID`;
- `LegalSource_ID`;
- `LegalDocumentFragment_ID`;
- `Bearer_Party_ID` and legal/normative role;
- beneficiary/counterparty role where directed obligation semantics require it;
- applicability/effective context;
- fulfilment/compliance state;
- consequence/remedy reference where applicable;
- override/supersession relation where applicable.

### G6 — Evidence, documents and records

Tender documents are governed records and SHALL be linked by controlled reference rather than duplicated as uncontrolled attachments where a governed repository object exists.

TMF667 Document semantics SHALL govern business-document references/versioning/interchange. Kongoni's adopted LegalDocML/Akoma Ntoso profile SHALL govern the legal/procurement document structure and stable governed fragment references used by this skill. Enterprise Records governance SHALL govern authoritative custody, version persistence, retention and disposition.

Mandatory evidence includes, as applicable:

- source tender / RFQ / RFP;
- addenda and clarifications;
- requirement compliance matrix;
- technical schedules;
- Product Specifications;
- Product Offering qualification evidence;
- pricing evidence and pricing-rule provenance;
- approvals;
- legal deviations and override authority;
- submitted response and proof of submission;
- award / regret correspondence;
- executed Agreement references;
- obligation compliance evidence.

### G7 — Internal submission approval

Submission is blocked unless:

- customer/party relationship validates;
- opportunity is qualified;
- all mandatory requirements have a resolved response state;
- all required Product Offering Qualifications pass or an authorised exception exists;
- all billable quote lines use governed Product/Product Offering records;
- all required billable quote lines are priced;
- all prices have approved provenance or authorised override;
- Agreement/Product Specification alignment passes or approved deviations are recorded;
- required legal/normative obligations are represented and traceable;
- technical and commercial schedules reconcile;
- required documents are current and controlled;
- bid authority and submission approval are recorded;
- submission deadline and method are verified.

### G8 — Submission and interaction management

Record submission as a governed business event and store proof of submission.

All post-submission clarifications, negotiations, BAFOs and customer interactions SHALL be recorded as Party Interactions and linked to the Opportunity, Quote, Tender and relevant Requirements.

Material price, scope, Product Offering, obligation or contractual changes require a new controlled Quote/Agreement version and renewed approval where applicable.

### G9 — Award / loss

Award SHALL create or bind the Agreement instance and downstream execution/order object.

A loss SHALL record structured loss reason, competitor/market evidence where lawfully known, pricing/technical findings and lessons learned.

Do not close the Tender at notification alone. Complete CHECK/STUDY, ACT, Record and controlled closure.

### G10 — Contract / order handoff

For awarded Tenders, verify that the executed Agreement, final Quote, Product Offering and Product/Order state reconcile before handoff.

Where a TMF622 Product Order equivalent applies, the ordered offering/product, quantity, site, asset/service context and agreed commercial terms SHALL trace back to the accepted Quote.

The executed Agreement SHALL trace to the applicable LegalDocument and LegalNorm representations for material obligations.

## 6. Information model

The Tender composite SHALL include references to, not copies of, the following governed information objects as applicable:

- Tender_ID;
- SalesLead_ID;
- SalesOpportunity_ID;
- Customer_ID;
- Party_ID(s);
- PartyRole_ID(s);
- LegalNormRole_ID(s);
- ValueStream_ID;
- ProductSpecification_ID(s);
- ProductOffering_ID(s);
- ProductOfferingPrice_ID(s);
- PricingRule_ID(s);
- ProductOfferingQualification_ID(s);
- Product_ID(s) where realised/transactional product identity is required;
- Quote_ID and Quote_Version;
- QuoteItem_ID(s);
- AgreementSpecification_ID;
- Agreement_ID where applicable;
- LegalDocument_ID(s);
- LegalDocumentFragment_ID(s);
- LegalNorm_ID(s);
- AgreementObligation_ID(s);
- ProductOrder_ID or downstream execution object where awarded;
- Requirement_ID(s);
- Document_ID(s);
- PartyInteraction_ID(s);
- Partner/Partnership_ID(s) where applicable;
- BidDecision_ID;
- Approval_ID(s);
- OverrideDecision_ID(s) where applicable;
- Task_ID(s);
- Evidence_ID(s);
- PDCA_Cycle_ID.

No CRM module, workflow screen, spreadsheet or document is a semantic parent of these business objects.

## 7. CRM operating model

Zoho CRM is the enterprise execution/control layer for Tender lifecycle transactions and state changes.

The CRM implementation SHALL support at least:

- Lead -> qualified Opportunity conversion or equivalent governed relationship;
- Tender as a procurement-event orchestration object linked to Opportunity rather than a replacement for Opportunity;
- customer and Party Role bindings;
- separate commercial Party Role and legal/normative role semantics;
- requirement register / compliance matrix;
- Product Specification / Product Offering / Product qualification relationships;
- governed Product/Product Offering lookup for every proposed billable line;
- governed price provenance and authorised override references;
- Quote versioning and approval;
- controlled Document and LegalDocumentFragment references;
- interaction history;
- Agreement and Agreement-obligation linkage;
- award/loss state and reason;
- downstream Order/contract handoff;
- task, evidence and PDCA links;
- immutable audit evidence for material state changes.

CRM implementation objects SHALL remain tertiary transactional representations where an enterprise semantic or normative object exists upstream.

## 8. Quote/Product/Agreement consistency rules

The following semantic relationship SHALL validate before submission:

`Value Stream -> Product Type -> Principal Agreement Type -> Contractual Role Type(s) -> Counterparty Relationship -> Entity/Agent`

The commercial transaction chain SHALL validate:

`Tender -> Opportunity -> Customer/Party -> Requirement -> ProductSpecification -> ProductOffering -> Qualification -> QuoteItem -> Quote -> AgreementSpecification -> Agreement -> ProductOrder`

The legal/normative traceability chain SHALL validate where applicable:

`SourceDocumentFragment -> TenderRequirement -> Agreement/LegalDocumentFragment -> LegalNorm -> Obligation/Permission/Prohibition -> ComplianceEvidence`

A broken mandatory relationship is a submission-blocking exception.

## 9. Business rules, authority and overrides

Machine-readable Tender business rules SHALL carry at minimum:

- `Rule_ID`;
- rule type;
- authority;
- normative/business source;
- version;
- status;
- effective date;
- applicability context;
- condition/antecedent;
- consequence;
- evidence requirement;
- override relation where permitted.

An exception SHALL NOT be represented only as a Boolean flag.

Where a rule may be overridden, the target relation is:

`ExceptionDecision -> OverrideRule -> BaseRule`

The override SHALL identify authority, scope, rationale, effective period and evidence.

Unauthorised overrides SHALL fail closed.

## 10. Compliance-state separation

The skill SHALL distinguish:

- `TenderRequirementCompliance` — whether the bid response satisfies the procurement requirement;
- `ProductOfferingQualification` — whether the offered proposition is technically/commercially eligible;
- `LegalObligationCompliance` — whether an Agreement/legal obligation has been fulfilled or remains compliant.

These states SHALL NOT be collapsed into one generic Compliance field.

## 11. B2B partner process

Where the bid depends on OEMs, dealers, subcontractors, consortium members, funders, insurers or service providers, treat them as governed Parties/Party Roles and, where the relationship itself is managed as a partnership, align to TMF668 Partnership Management semantics.

Partner commitments required for the submitted offer SHALL have evidence, validity period and authority. An assumed partner commitment is not valid evidence.

## 12. Bid/no-bid decision

The bid/no-bid decision SHALL consider at minimum:

- strategic/value-stream fit;
- Product Specification/Product Offering fit and qualification;
- customer/counterparty eligibility;
- technical compliance;
- commercial viability;
- capacity and delivery feasibility;
- legal/contract deviation risk;
- funding/credit requirements;
- partner dependencies;
- deadline feasibility;
- probability of win;
- expected risk-adjusted economic value.

The decision SHALL be `BID`, `NO_BID`, or `ESCALATE`, with authority and rationale recorded.

## 13. PDCA execution

Every material Tender follows:

`Mandate -> PLAN -> Authorisation -> DO -> Evidence -> CHECK/STUDY -> ACT -> Record -> Close or Replan`.

T0 informational Tender lookups may be answered directly.

T1 controlled Tender updates require evidence and validation.

T2 material bid, price, Product Offering, Agreement, submission or CRM-state changes remain OPEN after DO until CHECK/STUDY passes and an ACT decision is recorded.

T3 critical changes include material contract deviations, unauthorised pricing overrides, post-submission economic changes, high-risk compliance exceptions or production-control changes.

`DO_COMPLETE != TASK_COMPLETE`.

A Tender SHALL NOT close merely because it is Awarded, Lost, Withdrawn or Cancelled. Closure requires the required CHECK/STUDY evidence, ACT decision, record updates and accountability-task updates.

## 14. CHECK/STUDY tests

Before submission or closure, perform as applicable:

- source-document completeness check;
- stable governed source-fragment/provenance check;
- requirement coverage and MECE check;
- mandatory Tender Requirement compliance check;
- Product Specification/Product Offering crosswalk;
- Product Offering Qualification check;
- TMF699 Sales Quote / TMF648 Quote identity and version reconciliation where both representations exist;
- Quote completeness and arithmetic check;
- CRM Product/Product Offering source check;
- ProductOfferingPrice/PricingRule provenance check;
- authorised override validation;
- Agreement/Product Specification alignment check;
- Agreement/LegalDocument/LegalNorm traceability check;
- obligation Bearer/authority/source/compliance mapping check;
- customer/party/commercial-role/legal-role relationship check;
- controlled Document/version/custody check;
- approval/authority check;
- deadline/submission-method check;
- duplicate Lead/Opportunity/Tender/Quote check;
- post-award Quote/Agreement/Order reconciliation;
- PDCA evidence/ACT/record closure check;
- regression check against prior approved versions.

## 15. ACT decisions

Use only:

- `ADOPT` — evidence supports the implemented state;
- `ADAPT` — remediation is required;
- `REPEAT` — rerun the controlled activity without changing the governing design;
- `REJECT` — proposed state is not acceptable;
- `ESCALATE` — authority, legal, commercial or technical decision exceeds delegated mandate.

## 16. Fail-closed controls

The skill SHALL block transition to `APPROVED_FOR_SUBMISSION`, `SUBMITTED`, or an equivalent externally binding state when any of the following is true:

- customer or Opportunity identity is unresolved;
- Tender close date is unresolved;
- a mandatory Requirement is unanswered or unresolved;
- a required source document/fragment cannot be traced;
- a billable Quote Line lacks a governed Product/Product Offering;
- a required billable line is unpriced;
- a price lacks approved ProductOfferingPrice/PricingRule provenance or authorised override;
- Product Offering Qualification contains an unresolved blocking failure;
- Quote terms conflict with the approved Agreement/Product Specification without an authorised deviation;
- required legal/normative obligations cannot be represented or traced;
- required evidence is missing, stale or rejected;
- submission authority is absent;
- a material post-approval change has not been re-approved;
- an exception has no valid override authority;
- a material lifecycle transition lacks required PDCA evidence.

Draft or work-in-progress states MAY contain incomplete data where the incompleteness is explicitly permitted by the lifecycle and does not result in external issue, submission or contractual commitment.

## 17. TM Forum + OASIS conformance position

TM Forum is the primary commercial-process, catalogue, qualification, quote, agreement, interaction and order interoperability reference.

Kongoni uses an enterprise-adopted OASIS LegalDocML/Akoma Ntoso profile for machine-readable legal/procurement document structure and stable fragment referencing. This is a Kongoni application of the OASIS standard; it is not asserted that OASIS prescribes a private B2B contract-management process.

OASIS LegalRuleML is the primary normative-rule reference for obligations, permissions, prohibitions, authority, legal sources, compliance and overrides.

The standards are complementary in this skill and SHALL NOT be collapsed into one ontology.

Kongoni-specific Tender and TenderRequirement objects are controlled extensions required to represent procurement-event orchestration and requirement compliance. These extensions SHALL preserve TM Forum semantics and map outward through applicable TM Forum resources rather than redefining Lead, Opportunity, Customer, Party, Product Specification, Product Offering, Qualification, Quote, Agreement, Document, Interaction or Order.

Kongoni Agreement, LegalDocument and LegalNorm objects SHALL preserve the separation between commercial transaction state, legal-document representation and normative-rule semantics.

Where a current stable standards version differs from an older design reference, implementation teams SHALL use the governed approved version or current stable version according to enterprise standards governance.

## 18. Skill boundary

This skill owns the Tender Management execution methodology, process gates, semantic mappings, required evidence, validation sequence and fail-closed control requirements.

It SHALL NOT define standing agent authority, credentials, delegated approval limits or system-access permissions. Those belong in the applicable Agent Contract.

It SHALL NOT require one monolithic Tender microservice. Deterministic validations, rule evaluation, pricing control, lifecycle transition enforcement, document-fragment resolution or handoff operations MAY be implemented as modular services under governed interfaces.

CRM, services and agents SHALL conform to this skill; none of them is the semantic parent of the skill's business objects.

## 19. Required outputs

A completed Tender cycle SHALL produce or update, as applicable:

- qualified Sales Opportunity and Tender record;
- governed requirement compliance matrix with source-fragment provenance;
- Product Specification/Product Offering/Product qualification crosswalk;
- governed Quote and Quote Lines;
- governed price/provenance record and any authorised override;
- Agreement/Product Specification crosswalk;
- LegalDocument and LegalNorm traceability for material contractual requirements;
- controlled Tender document references;
- approval and submission record;
- customer interaction / clarification record;
- award/loss result;
- downstream Agreement/Order handoff where awarded;
- obligation/compliance evidence where applicable;
- PDCA evidence, CHECK/STUDY result and ACT decision;
- accountability task and authoritative record updates.

## 20. Zoho CRM object mapping

This section defines the required transactional mapping. CRM objects are tertiary execution/control representations and SHALL NOT become semantic parents.

| Skill / reference object | Current Zoho CRM object | Mapping status | Required control |
|---|---|---|---|
| SalesLead | `Leads` | DIRECT | Retain Lead as pre-qualification commercial signal. |
| SalesOpportunity | `Deals` | DIRECT | `Tenders.Qualified_Deal` SHALL reference the authoritative Deal/Opportunity. |
| Tender | `Tenders` | DIRECT KONGONI EXTENSION | Retain as procurement-event orchestration object; do not duplicate Deal authoritative sales state. |
| Customer / procuring organisation | `Accounts` via `Tenders.Procuring_Account` | DIRECT TRANSACTIONAL PROJECTION | Account is not the semantic parent of Party. |
| Party / commercial PartyRole / relationship | `Accounts`, `Contacts`, `PartyRoles`, `PartyRelationships` | COMPOSITE | Bind buyer, OEM, partner, subcontractor, funder and other roles explicitly. |
| TenderRequirement | `TenderRequirements` | DIRECT KONGONI EXTENSION | Keep `TR-*` identity; add governed source-fragment and downstream object relations. |
| Source Document | controlled document record plus current `Document_Folder_ID` / `Source_Document_ID` references | PARTIAL | Replace free-text-only identifiers with governed Document lookup/reference where available. |
| LegalDocumentFragment | no complete dedicated CRM object evidenced | GAP | Add governed fragment reference/object; retain clause/page only as human locator. |
| ProductSpecification | `ProductSpecifications` | DIRECT | Requirement and Offering SHALL resolve to specification. |
| ProductOffering | `ProductCatalogues` + `Products` currently approximate the transactional layer | GAP / ADAPT | Do not equate Product with Offering. Introduce explicit ProductOffering identity/object or governed relation without duplicating Product Master. |
| ProductOfferingPrice | Price Books / Product pricing fields are implementation mechanisms | GAP | Add governed price identity/provenance object or relation with effective date/context/rule. |
| ProductOfferingQualification | `ProductQualifications` | DIRECT / RELATIONSHIP GAP | Add direct binding from TenderRequirement and ProductOffering to qualification result. |
| Product / realised or transactional product | `Products` | DIRECT TRANSACTIONAL | Billable lines SHALL resolve to active governed Product/ProductOffering representation. |
| Quote | `Quotes` | DIRECT | Treat CRM Quote as authoritative TMF648-aligned commercial quotation transaction. |
| QuoteItem | `Quotes.Quoted_Items` subform | DIRECT | Every billable line must bind Product/ProductOffering and approved price provenance. |
| TMF699 Sales Quote view | no separate authoritative object required | DERIVED / REFERENCE | If represented, cross-reference `Quotes` identity/version; prohibit duplicate commercial truth. |
| AgreementSpecification | `Agreement_Classes` / governed agreement-type/specification layer | PARTIAL | Bind Tender/Quote to applicable Agreement Specification before submission. |
| Agreement | `Agreements` | DIRECT TRANSACTIONAL PROJECTION | Use as authoritative CRM transaction record, not sole legal-document representation. |
| CustomerAgreement | `CustomerAgreements` | DUPLICATION RISK | Treat as relationship/view or retire/merge authority where it duplicates `Agreements`; do not maintain two authoritative agreement truths. |
| AgreementObligation | `AgreementObligations` | DIRECT / SEMANTIC ADAPT | Add LegalNorm, Bearer, source fragment, applicability, compliance and override semantics. |
| Agreement-Product relation | `Agreement_Products` | DIRECT | Preserve Product/Offering contractual binding. |
| Agreement-Asset relation | `Agreement_Assets` | DIRECT | Use for machine/asset-specific contractual identity. |
| Party Interaction | `CustomerCommunications` plus CRM Calls/Emails/Meetings/Messages | COMPOSITE | Material tender interactions SHALL link Tender, Deal, Quote and Requirement. |
| Governed approval | `GovernedApprovals` | DIRECT / RELATIONSHIP GAP | Bind bid/no-bid and submission approval to Tender and Quote version. |
| ProductOrder | `Sales_Orders` | DIRECT | Awarded path SHALL reconcile accepted Quote/Agreement before Order handoff. |
| ProductOrderItem | `Sales_Orders.Ordered_Items` | DIRECT | Trace to accepted Quote Item and Product Offering. |
| Task / accountability | `Tasks` | DIRECT | Material tasks SHALL reference Tender/Requirement and PDCA cycle. |
| LegalNorm / machine-readable business rule | no single CRM module SHALL be assumed canonical | EXTERNAL/SHARED GOVERNED OBJECT | CRM may store rule references; canonical LegalRuleML/business-rule representation remains upstream. |
| ComplianceEvidence | document/evidence references plus TenderRequirement evidence fields | PARTIAL | Evidence SHALL be governed, versioned and traceable to the applicable Requirement/Qualification/Obligation. |
| PDCA_Cycle | task/evidence fields and governed execution records | GAP / ADAPT | Add explicit PDCA cycle reference and CHECK/STUDY/ACT closure bindings for material Tender work. |

### 20.1 Current Tenders field remediation

The current `Tenders.Workflow_Stage` contains useful operational values but mixes lifecycle state, process substate and gate/decision outcomes. It SHALL be normalised as follows:

- `Discovered` -> `DISCOVERED`;
- `Documents Acquired` -> `Process_Substate = DOCUMENTS_ACQUIRED` while lifecycle remains `QUALIFYING`;
- `Requirements Under Review` -> `QUALIFYING`;
- `Eligibility Hold` -> `GateStatus = HOLD`;
- `Eligibility Passed` -> `QUALIFIED` with qualification `PASS`;
- `Bid No Bid Review` -> `BID_DECISION`;
- `Bid Approved` -> `BidDecision = BID` plus approval reference;
- `Bid Preparation` -> `BID_IN_PREPARATION`;
- `Compliance Check` -> `INTERNAL_REVIEW`;
- `Ready for Submission` -> `APPROVED_FOR_SUBMISSION` only after G7 passes;
- `Submitted` -> `SUBMITTED`;
- `Clarification Evaluation` -> `CLARIFICATION_NEGOTIATION`;
- `Awarded` -> `AWARDED`;
- `Unsuccessful` -> `LOST`;
- `Withdrawn` -> `WITHDRAWN`;
- `Cancelled` -> `CANCELLED`;
- add `CONTRACTING`, `ORDER_HANDOFF`, `CHECK_STUDY`, `ACT`, `CLOSED` or equivalent governed lifecycle/closure representation.

`Tenders.Originating_Lead`, `Tenders.Qualified_Deal`, `Tenders.Procuring_Account`, `Closing_DateTime`, `Source_URL`, `Source_System`, `Primary_Value_Stream`, `Document_Folder_ID` and `Reissue_Of` SHALL remain useful transactional attributes/relationships, subject to the stronger governed relationships above.

### 20.2 Current TenderRequirements field remediation

Existing `TenderRequirements` controls for source document, source clause/page, requirement type, requirement class, mandatory flag, evaluation weight, responsible owner, required evidence, evidence status, compliance result, exception status, due date, response reference and evidence reference SHALL be retained.

Add or bind the following governed relationships:

`TenderRequirement -> SourceDocument -> SourceFragment`

`TenderRequirement -> ProductSpecification -> ProductOffering -> ProductOfferingQualification`

`TenderRequirement -> QuoteItem`

`TenderRequirement -> AgreementSpecification / AgreementObligation -> LegalNorm`

Separate the existing generic `Compliance_Result` use into the three governed semantics defined in section 10 rather than reusing one status for Requirement compliance, Product Offering Qualification and Legal Obligation compliance.

### 20.3 CRM fail-closed submission rule

The CRM Blueprint/workflow SHALL NOT permit Tender transition to `APPROVED_FOR_SUBMISSION` or `SUBMITTED` unless the following resolve true:

`OpportunityQualified AND CustomerResolved AND MandatoryRequirementsResolved AND ProductOfferingQualificationsPassed AND RequiredQuoteLinesPriced AND QuoteLinesUseGovernedProducts AND PriceProvenanceValid AND AgreementAlignmentPassed AND ControlledEvidenceCurrent AND SubmissionApprovalRecorded`.

This rule is a transactional implementation of the Skill. The machine-readable governing rule remains separately identifiable and version-controlled.
