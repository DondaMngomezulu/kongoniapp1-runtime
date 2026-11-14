# Reusable governed object controls — review-only extension

**Approval scope:** CEO accepted the *proposed design* on 20 October 2026 and requested reuse across other governed objects before final tests/publication. This does **not** bypass independent canonical registration, system-owner review, security validation or actual release. Do not promote source records under HOLD.

## Common controls, applied once and inherited across objects

| Shared control | Reuse scope | Engineering proof required |
| --- | --- | --- |
| Identity and semantic classification | All objects: Account/Contact/Party, Lead/Deal, Product/Offering, Quote, Agreement, Invoice, Tender, Document, Communication | Preserve existing canonical ID, object type, role, code-list version and source; semantic type is not a CRM module name |
| Source provenance | All | Authoritative repository, source URI/version, effective interval, hash/evidence; unverified fact becomes review claim |
| Status and change lifecycle | All | DRAFT/CHECK/HOLD/release state mapped to governed Genericode, never inferred from CRM active flags |
| Template, document, channel | Messages and documents | Published template ID/version, merge rule, legal entity, attachment hash and correct channel; no duplicate identities |
| Assumptions, exceptions and clarifications | Quotes, offers, RFQs, contracts, credit decisions, tenders, reports | Proposed vs accepted terms; documented override, conflicting source resolution and named sign-off |
| Pricing and units | Products, rates, Quote Items, Orders, Invoices | Price source/effective date, product offering, UOM, tax basis, line/total reconciliation; no provisional rate issue |
| Finance/credit authority | Leases, instalment sales, structured funding, receivables | Separately approved underwriting, instrument type and finance role; no implication from screening/payment terms |
| Issuer, recipient and party roles | Commercial/legal documents and all outbound communications | Verified GroupEntity and party roles, exact authorised recipient, signature/approval and channel consent |
| Conditions and dependencies | Tenders, contracts, delivery, purchases, finance | Eligibility, agreement/PO dependencies, technical compliance, returnables and prerequisite evidence |
| Immutable release and audit | All externally issued or production-applied objects | Reviewer separation, approved snapshot hashes, audit receipt, idempotency and independent readback |

**Cross-object overlay inheritance:** Common controls are references to verified concepts, not new fields or legal classifications. Object-specific overlays retain separate meanings: quotations use UBL Quotation / TMF Quote interoperability as applicable; invoices use UBL Invoice, payments accounting/ISO20022 as applicable; agreements use operative legal templates and classification; tenders use procurement rules and returnables; products/specifications use OEM facts; communications use MRG-CVR-001 and applicable TMF681/683; BIAN is a financial-domain reference rather than a generic message XSD. Pin adopted exact edition and applicability before release.

## Confirmed CRM object APIs (20 October 2026 readback)

- Prospect/customer: `Leads`, `Accounts`, `Contacts`, `Deals`.
- Catalogue: `Products`, `ProductSpecifications`, `ProductOfferings`, `ProductOfferingPrices`, `ServiceOfferings`.
- Commerce: `Quotes`, `Quoted_Items`, `Sales_Orders`, `Purchase_Orders`, `Invoices`.
- Contracts and document metadata: `Agreements`, `Agreement_Templates`, `BusinessDocumentTypes`, `CustomerDocuments`.
- Procurement/compliance: `Tenders`, `TenderRequirements`.
- Party/legal identities and fulfilment: `GroupEntities`, `FulfilmentEvents`.
- Messaging: `CustomerCommunications`.

Mappings are **source bindings**, not assertions of ISO/TMF/UBL semantic equivalence. A verified CRM API field does not prove a populated record, an approved concept or functioning release control.

## Reusable review cases

| Scenario | Shared property | Domain guard |
| --- | --- | --- |
| Loakantse quotation enquiry | Qualification identity, technical claims and unagreed assumptions | D6 vs D155 unresolved; Account cannot issue quote; 250h default is not an accepted customer term |
| Nomatiki finance lease | Customer identity, product specs, credit/proposal and approval evidence | Finance product, underwriting and equipment prices separately required |
| Constructo lease/rental | Offering terms version, line price, VAT, term and purchase option | Contract model and balloon/WACC cannot be inferred or combined with rental |
| Gert Sibande tender | Counterparty/site, tender IDs, submission and returnables | Compulsory briefing eligibility/attendance cannot be assumed |
| XCMG equipment sale | Products, seller party, approved pricing and payments | Contract operative precedence and payment provisions control, not message copy |
| Invoices/orders | Approval/version/issuer/party, UOM, monetary and audit controls | Invoice/accounting and ordering have different taxable event, legal and fulfilment requirements |

## Governance publication / execution gates

1. Compare to existing enterprise dictionary, standards, RegRep/Genericode and role/identifier register. Reject unresolved or duplicate new concept IDs.
2. Run JSON Schema 2020-12 structural tests and adversarial cross-object examples (synthetic, no private records).
3. Review source/value/authority/semantics and stage-specific exception precedence with Data Steward, Commercial/Legal, CRM and Document Control.
4. Validate ArchiMate business-layer relationships and SysML v2 systems requirements and trace to GitHub technical implementation.
5. Conduct CRM/LibreDocs/ODF merge, UBL-specific XSD/profile validation, real price and approval readback, channel/permission/bypass tests in Development.
6. GitHub PR review and controls including `CTL-DEV-CHG-LOG-001`; independent ACT approval and publication to authoritative register; **only then** controlled production change with rollback/readback.

This change is a **source-controlled candidate extension** and is not a second canonical register, not a live CRM implementation and not permission to issue customer communications. See [PR #72](https://github.com/DondaMngomezulu/kongoniapp1-runtime/pull/72), related [#54](https://github.com/DondaMngomezulu/kongoniapp1-runtime/issues/54) and [#67](https://github.com/DondaMngomezulu/kongoniapp1-runtime/issues/67).
