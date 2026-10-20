# Quotation-covering communications — CRM-bound candidate profile

**Lifecycle:** CHECK/STUDY REVIEW ONLY; **not deployed, approved for production, or issued to customers**. This proposal reuses existing governed objects and must not allocate a new canonical message, schema, template or value-stream identifier.

## Source authority and existing identities

| Role | Existing authority/ID | Observed state |
|---|---|---|
| Merge rule | [MRG-CVR-001 v1.0](https://docs.google.com/document/d/13gOyII96BswC7z5SioCfE7YAjjyE3KyWDRGJO5AwmTk/edit) (GOV-APR-10, 9 Oct 2026) | Adopted field dictionary and release rules |
| Master message register | [Enterprise Message Schema Register](https://docs.google.com/spreadsheets/d/1TlHa9Q43Y-xJr-QJN4QveO0TKhT9hwm13K0wpX6BGVI/edit), ROR-0095 | Controlled draft; canonical register ID and approval pending |
| Existing issued-quotation cover | \`Agreement_Templates\` record \`5643538000010621018\`, \`TPL-FINCO-UBL-QUO-001-CVR\` | Template_Status Controlled; Review_Status adopted; renderer **Not Configured** |
| Existing issued parent | \`Agreement_Templates\` record \`5643538000008959040\`, \`TPL-FINCO-UBL-QUO-001\` | Publication and rendered-instance checks still required |
| Qualification-stage email | \`VS02-02 Qualification Information Request\`, CRM email template \`5643538000009733101\` | Leads module; existing scenario \`VS02-QUA-QIR-QCL-V01\` |
| Requirements confirmation | \`VS02-03 Requirements Confirmation\`, CRM email template \`5643538000009732101\` | Deals module; existing scenario \`VS02-REQ-RCF-PSS-V01\` |
| Business document | [REG-KNG-BDT-001](https://docs.google.com/spreadsheets/d/1OxgfobMF19ZrWg6pLuuhG_ZZNiTVUtcQgdEdSXEXw78/edit) \`BDT-1006\` | A Quotation document is not an email transport envelope; existing UBL edition migration HOLD |
| Release control | [GitHub #67](https://github.com/DondaMngomezulu/kongoniapp1-runtime/issues/67), [#54](https://github.com/DondaMngomezulu/kongoniapp1-runtime/issues/54) | No production-universal send interceptor evidenced |

## Two controlled stages — no category overlap

**Stage A: Prequote qualification or requirements confirmation.** A \`Leads\` or verified \`Deals\` instance is authoritative. Use the appropriate existing VS02 qualification/requirements scenario, augmented by the six-section *candidate* content pattern. This is a clarification and nonbinding technical/commercial-basis summary. It SHALL NOT imply that an approved quote, price, rental capacity, credit facility or equipment commitment exists, and SHALL NOT attach an unapproved quotation.

**Stage B: Issued quotation cover.** After conversion and authorisation, use the existing \`TPL-FINCO-UBL-QUO-001-CVR\` child and actual published \`TPL-FINCO-UBL-QUO-001\` rendered parent. Require an approved \`Quotes\` instance, verified issuer and account, effective approved pricing per quote line, independent document publication and formal send approval. Do not use the candidate six-section pattern to bypass the adopted \`MRG-CVR-001\` v1.0 placeholder grammar or source status.

A changed message purpose requires a controlled scenario selection. The preliminary and issued messages are distinct instances, sharing the same enterprise concepts but not a common release permission.

## Reusable six-section message structure

1. **Our understanding of requirements** — source RFQ/site technical scope, quantity, machine class, usage, dates, term, responsibilities; label conflicts rather than silently resolving them.
2. **Assumptions** — proposed and applicable \`ProductOfferings\` terms, minimum usage, fuel, operators, maintenance, payment, credit and mobilisation; cite term source/version and identify deviations.
3. **Technical offer** — \`ProductSpecifications\` and \`Quoted_Items\` technical configuration; safety, staffing, mechanical availability, backup equipment; never assume OEM equivalence.
4. **Finance offer** — distinguish routine rental payment/credit terms from a separate finance lease, instalment sale or operating lease; no funding approval inferred from an enquiry or bureau report.
5. **Commercial offer** — approved \`ProductOfferingPrices\` and \`Quoted_Items\`, hourly UOM, minimum, unit/line totals and once-off charges; prequote copy omits prices until approved.
6. **Points for clarification** — sourced technical contradictions, contracting roles, eligibility, utilisation and billing exceptions, site services, technical compliance and deadlines; track answers and revision.

This pattern is a content extension proposal, **not** a silently amended \`MRG-CVR-001\` v1.0. New section-level merge tokens must first be approved in the proper versioned merge dictionary; until then, use controlled CRM-backed composition with complete value and evidence checks.

## CRM information-object crosswalk

| Concept | CRM source/API (verified from live metadata 20 Oct 2026) | Rule |
|---|---|---|
| Prospect, correspondence and authorised recipient | \`Leads.First_Name\`, \`Leads.Full_Name\`, \`Leads.Company\`, \`Leads.Email\`, \`Leads.Product_Enquiry_Notes\`; after conversion \`Contacts\`, \`Accounts\` | Do not conflate sender address with authorised customer contact; reconcile identity evidence |
| Opportunity and requirements | \`Deals.Deal_Name\`, \`Deals.Missing_Required_Inputs\`, \`Deals.Originating_Lead\`; source RFQ and technical scopes | A Deal may be absent; use Lead workflow instead of synthetic Deal fields |
| Customer eligibility | \`Accounts.Account_Name\`, \`Accounts.Can_Issue_Quotes\` | Must be true before *formal* issued quotation |
| Quotation and release | \`Quotes.Quote_Number\`, \`Quotes.Quote_State\`, \`Quotes.Release_Status\`, \`Quotes.Valid_Till\`, \`Quotes.Issuing_Group_Entity\` | Require approved transaction, legal issuer, validity and published document evidence |
| Quoted equipment | \`Quoted_Items.Product_Name\`, \`Quantity\`, \`Product_Specification\`, \`Product_Offering\`, \`Offering_Price\`, \`Pricing_Rule_ID\`, \`Price_Provenance\` | Never treat customer-stated model as approved equivalent equipment |
| Governed product offering | \`ProductOfferings.Offering_ID\`, \`Contract_Model\`, \`Terms_Version\`, \`Terms_Status\`, \`Terms_Approved\`, \`Labour_Basis\`, \`Parts_Basis\`, \`Payment_Basis\` | Versioned term overrides only if authorised; rental does not become financing because payment is monthly |
| Approved price | \`ProductOfferingPrices.Unit_Price\`, \`Price_Status\`, \`Effective_From\`, \`Effective_To\`, \`Pricing_Rule_ID\`; \`Quotes.Sub_Total\`, \`Grand_Total\` | No rates from provisional QA sheets; quote monetary values exclude invoice-only VAT calculation |
| Technical authority | \`ProductSpecifications.Specification_Version\`, \`Spec_Status\`, \`Current_Approved\`, \`OEM_Model\`, \`Description\` | Versioned, evidenced OEM spec and technical qualification |
| Issuing entity | \`GroupEntities.Legal_Name\`, \`Trading_Name\`, \`Registration_Number\`, \`Public_Email\` | Contracting entity, not group brand or agent, supplies the signature |
| Stock and delivery evidence | \`FulfilmentEvents.Product\`, \`Event_Type\`, \`Event_Status\`, \`Quantity\`, \`Location\`, \`Event_Time\`; \`Quotes.Delivery_Programme\` | Mandatory Durban Received/Planned differentiation for relevant XCMG offer; planned is not in stock |
| Message instance and approval | \`CustomerCommunications.Governed_Msg_Template_ID\`, \`Template_Version\`, \`Quote\`, \`Contact\`, \`Account\`, \`Approval_State\`, \`Approval_Evidence\`, \`Delivery_Status\`, \`External_Message_ID\` | Preserve communication ID, identity, version, channel, approval and provider receipt; no send inferred from draft |

## Fail-closed release checks

- Reuse immutable approved template and parent IDs/versions; matching names alone are not acceptable; record source registry and output hash. 
- Validate ALL \`MRG-CVR-001\` placeholders, authorised sender, recipient and appropriate consent/channel; no unresolved placeholders, unsupported fields or unseen status overrides.
- For prequote: no representation of formal issued quotation, approved price or credit. Allow internal **draft review** under existing qualification scenario; send requires independently validated permitted template and CRM authority.
- For issued quote: \`Accounts.Can_Issue_Quotes=true\`, approved \`Quotes.Release_Status\`, approved source-effective \`ProductOfferingPrices\`, valid \`Quoted_Items\`, approved machine availability, and a genuinely published, rendered parent document attached.
- Do not use 250h default as accepted where client schedule conflicts; finance offer must not imply facility approval. Unresolved contractual party, D6/D155 class conflict and buyer eligibility remain explicit clarification facts.
- Trace \`CustomerCommunications\` approval and provider receipt. Universal send path (CRM UI/API, agent, WhatsApp, mass mail) remains blocked pending independent enforcement tests described in #67.

## Architecture trace and exit criteria

Business: ArchiMate Business Process **Lead qualification → Requirements confirmation → Quotation preparation → Commercial and documentary approval → Communication issuance**. Reuse Party, Product Offering, Quote, Communication and Agreement business objects; separate commercial offer from credit underwriting.

Systems: SysML v2 candidate requirement/verification chain for field presence, source identity and version, pricing parity, template parent, channel/consent, one successful synthetic render per stage, negative rejection for identity mismatch, no-quote, unapproved rate, unapproved issuer, invalid technical class and missing receipt. Bind Zoho CRM Functions/Blueprint and any approved outbox implementation through GitHub-controlled rules; **design is not deployment**.

Reviewer exit: Document Controller approves message identity/version and source template; CRM owner verifies the exact live merge rendering and send restrictions; Pricing/Credit approve applicable price/financing facts; Data Steward registers missing Genericode codes; Systems Architecture reviews ArchiMate/SysML and negative tests; authorised deployment/rollback and independently verified readback before production release.

No customer records, actual contact details, live quotes, credentials or prices are stored in this repository artifact.
