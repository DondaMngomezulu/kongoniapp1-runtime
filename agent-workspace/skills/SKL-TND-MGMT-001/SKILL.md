---
name: tender-management-b2b-tmforum
governed_id: SKL-TND-MGMT-001
version: '1.0'
status: ADOPTED_FOR_DEVELOPMENT
owner: Chief of Accountability
business_domain: B2B tender and bid management
methodology: MET-PDCA-001
primary_reference_model: TM Forum ODA / eTOM B2B sales process
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
  - Kongoni enterprise Product, Agreement, Counterparty, Value Stream and Task governance
---

# Tender Management Skill — TM Forum B2B Process

## 1. Purpose

Use this skill to govern business-to-business tender, RFQ, RFP, bid and proposal work from discovery through award, agreement formation and order handoff.

The skill SHALL treat tender management as a B2B sales process specialization aligned to TM Forum ODA/eTOM and Open APIs. It SHALL NOT create a competing enterprise sales lifecycle.

A Tender is a Kongoni governed business object that packages a customer procurement event and its evidence. It is not asserted to be a native TM Forum canonical resource. Its primary semantic anchor is the TM Forum Sales Opportunity, with related Quote, Customer/Party, Product Offering, Agreement, Document, Interaction and Order objects.

## 2. Canonical semantic mapping

The mandatory mapping is:

- external procurement notice / detected commercial interest -> TMF699 Sales Lead where qualification is not yet complete;
- qualified tender / RFQ / RFP pursuit -> TMF699 Sales Opportunity;
- procuring organisation -> TMF629 Customer and/or TMF632 Party, with TMF669 Party Role where role semantics are required;
- tender requirement line -> customer requirement mapped to Product Offering / Product Specification and qualification evidence;
- proposed commercial line -> TMF620 governed Product Offering / Kongoni CRM Product;
- feasibility / eligibility / technical fit -> TMF679 Product Offering Qualification or equivalent governed qualification result;
- commercial response -> TMF648 Quote;
- contract framework / award instrument -> TMF651 Agreement / Agreement Specification;
- tender pack, RFQ, clarifications, drawings, schedules and submission evidence -> TMF667 Document references and governed records;
- clarification, bidder communication and negotiation touchpoint -> TMF683 Party Interaction;
- successful award / executable demand -> TMF622 Product Order or governed downstream order/contract execution object;
- consortium, OEM, subcontractor or strategic partner involvement -> TMF668 Partnership plus Party / Party Role relationships as applicable.

The Tender object SHALL retain cross-references to these canonical objects and SHALL NOT duplicate their authoritative state.

## 3. B2B tender lifecycle

The standard lifecycle is:

`DISCOVERED -> QUALIFYING -> QUALIFIED -> BID_DECISION -> BID_IN_PREPARATION -> INTERNAL_REVIEW -> APPROVED_FOR_SUBMISSION -> SUBMITTED -> CLARIFICATION_NEGOTIATION -> AWARDED | LOST | WITHDRAWN | CANCELLED -> CONTRACTING -> ORDER_HANDOFF -> CLOSED`

Lifecycle states are commercial process states, not document statuses.

A tender may not advance to `QUALIFIED` until the prospect/customer, procurement event, due date, scope, value stream, target product family and minimum eligibility evidence are identified.

A tender may not advance to `APPROVED_FOR_SUBMISSION` unless the quote, product, agreement and evidence controls below pass.

## 4. TM Forum B2B process gates

### G1 — Lead / Opportunity qualification

Confirm:

- source and procurement-event identity;
- customer/party identity;
- buying organisation and relevant party roles;
- tender close date and submission channel;
- opportunity owner;
- target value stream and product family;
- commercial interest and strategic fit;
- mandatory eligibility criteria;
- bid/no-bid decision authority.

If the commercial interest is detected but the tender is not yet sufficiently qualified, keep it as Lead. Once the buyer and commercial pursuit are confirmed, promote to Sales Opportunity semantics.

### G2 — Requirement decomposition

Parse the procurement pack into individually traceable requirements.

Every requirement SHALL have:

- `Requirement_ID`;
- source document and source location;
- requirement type;
- mandatory / optional / scored classification;
- response owner;
- compliance state;
- evidence reference;
- related Product / Product Offering / Product Specification where applicable;
- related Agreement clause or legal obligation where applicable.

Requirements SHALL be MECE at the level used for bid compliance checking.

### G3 — Product qualification

Every offered line SHALL resolve to a governed CRM Product and canonical Product ID.

The skill SHALL use TMF620 Product Catalog semantics for offerable product structure and TMF679 Product Offering Qualification semantics for feasibility / eligibility assessment.

No free-text billable product may be introduced directly into a Quote.

If the required product does not exist, create or remediate the governed Product Master before quotation approval.

### G4 — Quote construction

The Quote is the authoritative commercial response object.

Every billable Quote Line SHALL reference:

- CRM Product ID;
- Canonical Product ID where required;
- quantity;
- usage unit;
- approved price or authorised pricing record;
- currency;
- tax basis;
- applicable customer / programme / site / asset context;
- related requirement ID(s).

A quote is invalid if any required billable line is blank, `TBC`, unresolved or unpriced.

The skill SHALL apply:

`BR-QUOTE-VALID-001: required_line_item_count = priced_required_line_item_count`

and:

`BR-QUOTE-LINE-SOURCE-001: every billable quotation line must reference an active governed CRM Product and an approved CRM pricing source or authorised exception.`

### G5 — Agreement alignment

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

### G6 — Evidence and document control

Tender documents are governed records and SHALL be linked by reference, not duplicated as uncontrolled attachments where a controlled repository object exists.

Use TMF667 Document Management semantics for document references/versioning/interchange and enterprise records governance for authoritative custody, retention and disposition.

Mandatory evidence includes, as applicable:

- source tender / RFQ / RFP;
- addenda and clarifications;
- requirement compliance matrix;
- technical schedules;
- product specifications;
- pricing evidence;
- approvals;
- legal deviations;
- submitted response and proof of submission;
- award / regret correspondence;
- executed agreement references.

### G7 — Internal submission approval

Submission is blocked unless:

- customer/party relationship validates;
- opportunity is qualified;
- all mandatory requirements have a response state;
- all billable quote lines are governed and priced;
- Product Offering Qualification has no unresolved blocking failure;
- Agreement alignment passes or approved deviations are recorded;
- technical and commercial schedules reconcile;
- required documents are current and controlled;
- bid authority is recorded;
- submission deadline and method are verified.

### G8 — Submission and interaction management

Record submission as a governed business event and store proof of submission.

All post-submission clarifications, negotiations, BAFOs and customer interactions SHALL be recorded as Party Interactions and linked to the Opportunity, Quote, Tender and relevant Requirements.

Material price/scope changes require a new Quote version and renewed approval.

### G9 — Award / loss

Award SHALL create or bind the Agreement instance and downstream execution/order object.

A loss SHALL record structured loss reason, competitor/market evidence where lawfully known, pricing/technical findings and lessons learned.

Do not close the tender at notification alone; complete CHECK/STUDY and ACT.

### G10 — Contract / order handoff

For awarded tenders, verify that the executed Agreement, final Quote and Product/Order state reconcile before handoff.

Where a TMF622 Product Order equivalent applies, the ordered product, quantity, site, asset or service context and agreed commercial terms must trace back to the accepted Quote and Product Offering.

## 5. Information model

The Tender composite SHALL include references to, not copies of, the following governed information objects:

- Tender_ID;
- SalesLead_ID where applicable;
- SalesOpportunity_ID;
- Customer_ID;
- Party_ID(s);
- PartyRole_ID(s);
- ValueStream_ID;
- ProductOffering_ID(s);
- Product_ID(s);
- ProductSpecification_ID(s);
- ProductOfferingQualification_ID(s);
- Quote_ID and Quote_Version;
- AgreementSpecification_ID;
- Agreement_ID where awarded;
- ProductOrder_ID or downstream execution object where awarded;
- Requirement_ID(s);
- Document_ID(s);
- PartyInteraction_ID(s);
- Partner/Partnership_ID(s) where applicable;
- BidDecision_ID;
- Approval_ID(s);
- Task_ID(s);
- Evidence_ID(s);
- PDCA_Cycle_ID.

No CRM module, workflow screen, spreadsheet or document is a semantic parent of these business objects.

## 6. CRM operating model

Zoho CRM is the execution/control layer for the tender lifecycle.

The CRM implementation SHALL support at least:

- Lead -> qualified Opportunity conversion or equivalent governed relationship;
- Tender as a pursuit/control object linked to Opportunity rather than a replacement for Opportunity;
- customer and party-role bindings;
- requirement register / compliance matrix;
- governed Product lookup for every proposed billable line;
- Quote versioning and approval;
- controlled document references;
- interaction history;
- agreement linkage;
- award/loss state and reason;
- downstream order/contract handoff;
- task and evidence links;
- immutable audit evidence for material state changes.

## 7. Quote/Product/Agreement consistency rule

The following relationship SHALL validate before submission:

`Value Stream -> Product Type -> Principal Agreement Type -> Contractual Role Type(s) -> Counterparty Relationship -> Entity/Agent`

and, at transaction level:

`Tender -> Opportunity -> Customer/Party -> Requirement -> Product Offering/Product -> Qualification -> Quote Line -> Agreement Specification -> Agreement/Order`

A broken mandatory relationship is a submission-blocking exception.

## 8. B2B partner process

Where the bid depends on OEMs, dealers, subcontractors, consortium members, funders, insurers or service providers, treat them as governed Parties/Party Roles and, where the relationship itself is managed as a partnership, align to TMF668 Partnership Management semantics.

Partner commitments required for the submitted offer SHALL have evidence, validity period and authority. An assumed partner commitment is not valid evidence.

## 9. Bid/no-bid decision

The bid/no-bid decision SHALL consider at minimum:

- strategic/value-stream fit;
- product fit and qualification;
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

## 10. PDCA execution

Every material tender follows:

`Mandate -> PLAN -> Authorisation -> DO -> Evidence -> CHECK/STUDY -> ACT -> Record -> Close or Replan`.

T0 informational tender lookups may be answered directly.

T1 controlled tender updates require evidence and validation.

T2 material bid, price, product, agreement, submission or CRM-state changes remain OPEN after DO until CHECK/STUDY passes and an ACT decision is recorded.

T3 critical changes include material contract deviations, unauthorised pricing overrides, post-submission economic changes, high-risk compliance exceptions or production-control changes.

`DO_COMPLETE != TASK_COMPLETE`.

## 11. CHECK/STUDY tests

Before submission or closure, perform:

- source-document completeness check;
- requirement coverage check;
- mandatory compliance check;
- Product Master crosswalk;
- Product Offering Qualification check;
- Quote completeness and arithmetic check;
- CRM Product/pricing-source check;
- Agreement/Product Specification alignment check;
- customer/party/role relationship check;
- document version/custody check;
- approval/authority check;
- deadline/submission-method check;
- duplicate opportunity/tender check;
- post-award Quote/Agreement/Order reconciliation where applicable;
- regression check against prior approved versions.

## 12. ACT decisions

Use only:

- `ADOPT` — evidence supports the implemented state;
- `ADAPT` — remediation is required;
- `REPEAT` — rerun the controlled activity without changing the governing design;
- `REJECT` — proposed state is not acceptable;
- `ESCALATE` — authority, legal, commercial or technical decision exceeds delegated mandate.

## 13. Fail-closed controls

The skill SHALL block submission when any of the following is true:

- customer or opportunity identity is unresolved;
- tender close date is unresolved;
- mandatory requirement is unanswered;
- a billable quote line lacks a governed CRM Product;
- a required line is unpriced;
- a price lacks an approved source or authorised override;
- a product is not qualified for the required application where qualification is mandatory;
- Quote terms conflict with the approved Agreement/Product Specification without an approved deviation;
- required evidence is missing or stale;
- submission authority is absent;
- a material post-approval change has not been re-approved.

## 14. TM Forum conformance position

This skill uses TM Forum as the primary B2B process and interoperability reference. Kongoni-specific Tender and Requirement objects are controlled extensions needed to represent procurement-event orchestration and compliance evidence.

The extensions SHALL preserve TM Forum semantics and map outward through the applicable TM Forum Open API resources rather than redefining Lead, Opportunity, Customer, Party, Product Offering, Qualification, Quote, Agreement, Document, Interaction or Order.

Where the current TM Forum stable Open API version differs from an older design reference, implementation teams SHALL use the current stable version unless a governed compatibility decision states otherwise.

## 15. Required outputs

A completed tender cycle SHALL produce or update:

- qualified Opportunity/Tender record;
- requirement compliance matrix;
- Product and qualification crosswalk;
- governed Quote and Quote Lines;
- Agreement/Product Specification crosswalk;
- controlled tender document references;
- approval and submission record;
- customer interaction / clarification record;
- award/loss result;
- downstream Agreement/Order handoff where awarded;
- PDCA evidence, CHECK/STUDY result and ACT decision;
- accountability task and record updates.
