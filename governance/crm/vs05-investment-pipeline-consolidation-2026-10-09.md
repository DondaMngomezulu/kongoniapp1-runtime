# VS05 Investment & Portfolio Value Realisation — CRM consolidation

Date: 2026-10-09
State: IMPLEMENTATION CHECK / STUDY, not governance approval.
Sources: BA-VS-001 (CEO-adopted value stream definition); CAT-ZCRM-CONFIG-001 (adopted CRM configuration metamodel); REG-INV-001 (staged holdings register).
References:
- https://docs.google.com/spreadsheets/d/1PqspV3b5alhRrFTXSov2jAGJW-EbD55C5UOC8XprERc/edit
- https://docs.google.com/spreadsheets/d/1kkMPCOz87JW3B37pCTW6zQ34mg36tVnjIOk0QNenkDw/edit

## Applied CRM configuration
- Existing public Deals Custom View `InvestDo / VS05 - Investment Pipeline` ID 5643538000008717181 retained.
- Criteria: `Owning_Value_Stream = VS05`. View columns now include `Source_URL`, `Source_Platform`, `Source_Listing_ID`, `Listing_Status` and `DD_Conclusion_Status`, in addition to established qualification, transaction type, stages, commercial amount and ownership.
- Readback: 46 Deals (previously 39) on 2026-10-09.
- Seven pre-existing recovered-equipment Deals had blank `Owning_Value_Stream`. Aligned to VS05 without changing their `InvestCo_Stage` values (`S1 Verified Lead`). CRM record readback confirmed seven updates.
- Existing public Leads view `InvestDo / VS05 - Candidate Leads` ID 5643538000008725103 retained with 69 leads; no change.
- Existing `InvestCo_Stage` S0-S15 reused. No new CRM module or pipeline stage created.

## Architectural boundaries
1. VS05 owns investment thesis, screening, investment decision, acquired investment position, portfolio governance and realisation.
2. VS02 owns financing origination, facility, funding, servicing, securitisation mechanics. Investment in senior debt into FinanceCo is a VS05 holding, but issuance/funding mechanics are VS02.
3. VS01 owns equipment sale/provision and physical asset access.
4. The `InvestmentMandates` CRM module lists investors/funding counterparties and must not be blended into buy-side investee opportunities.
5. The separate `REG-INV-001` represents staged or executed investment positions and financial/accounting governance, not all candidate Leads or Deals.
6. `Owning_Value_Stream` text VS05 is the current view-filter binding; `Governed_Value_Stream` picklist is the governed semantic binding. Differences require controlled reconciliation rather than bulk overwrites.

## Remaining CHECK/STUDY controls
- Existing Deals view contains `DUP:` and `UNQ:` placeholders. Reconcile canonical identity and source before record deletion/merge; preserve original IDs.
- Classify strategic funding prospects, supplier financing facilities and deal-sourcing investees separately; source hyperlinks do not constitute a confirmed seller offer or valuation.
- Verify original case/listing URL for recovered equipment deals, especially truncated Manong case link.
- Validate S0-S15 state transitions and DD/IC approval authority. Existing CEO approval process governs schema/object activation and is NOT an investment committee decision.
- No new approved enterprise code values/URIs without SCOPE-002 and live dictionary approval.
- Deploy any additional workflow/approval rules through sandbox test, signed decision and confirmed readback.
- Existing `InvestmentMandates` module is used for counterparty mandates; no new module required.

## PDCA
DO: CRM view updated and seven deal owners aligned.
CHECK: CRM view metadata and seven updated records read back; count moved 39 -> 46.
STUDY: Data quality, duplicate master, stage-mapping and investment approval controls remain open.
ACT: No CEO approval represented here, no automatic activation of new controlled processes and no investment approval granted.
