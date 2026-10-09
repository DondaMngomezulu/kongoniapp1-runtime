# Message-to-CRM binding diagnostics — 2026-10-10 (engineering only)

Issue: https://github.com/DondaMngomezulu/kongoniapp1-runtime/issues/57

This is an **architecture and test contract**, not CRM data, a promoted registry, or production approval.

Source: [REG-KNG-BDT-001](https://docs.google.com/spreadsheets/d/1OxgfobMF19ZrWg6pLuuhG_ZZNiTVUtcQgdEdSXEXw78/edit) REG-BDT-016/017; message register [controlled draft](https://docs.google.com/spreadsheets/d/1TlHa9Q43Y-xJr-QJN4QveO0TKhT9hwm13K0wpX6BGVI/edit).

Read-only CRM findings (12 module metadata inventories, 2026-10-10):
- Agreement_Templates.Document_Type1 is a **picklist**, although the register's template lookup heading implies a lookup. Review the business relationship before changing configuration.
- CustomerDocuments.Registration_Date and Source_Reference were not returned by the live CRM field inventory. Do not assume substitute fields.
- BusinessDocumentTypes.Document_Type_ID = autonumber; Accounts.Account_Name and EquipmentAssets.Name = text. The register says LOOKUP in the *binding role*. These are not automatically native CRM lookup fields. Distinguish ID-based cross-reference resolution from real lookup types.
- Quotes.Quoted_Items = mandatory subform; test child rows separately.
- Five schema bindings SB-0001, SB-0002, SB-0003, SB-0004 and SB-0006 remain NOT_TESTED / NOT_VERIFIED on the live message register. The synthetic fixtures here test **only the contract shape**, not OASIS XSD conformance or runtime readback.

Admission gate:
1. Verify exact applicable UBL 2.4 vs adopted 2.5 normative XSD and migration authority.
2. Resolve field source and data type; identify native lookup versus identifier dereference. Make no silent replacement.
3. Verify CRM template versions, merge field existence, entity/role/consent, approver and document attachments.
4. Validate machine payloads against actual XSD/enterprise profiles, positive/negative cases, source versions, and canonical event envelope.
5. Conduct authenticated **Development-only** end-to-end test with CRM and Catalyst receipts; no customer sends.
6. Demand explicit deployment authority, evidence, GitHub checks and ACT approval before Production.

The fixture values are synthetic and structurally grounded in the existing five binding IDs. CI success is **not** approval or release evidence.
