# ADR-VS05-REPOSITORY-BOUNDARY-001 — Investment Pipeline Information Placement

## Status
PROPOSED — implementation guidance; formal adoption remains subject to the authorised enterprise architecture change-control process.

## Decision
The GitHub repository is an **architecture and configuration-as-code** repository. It SHALL NOT store operational or transactional business records, investment leads, actual investment holdings, CRM data extracts, individual deal information, counterparties' confidential information, financial transaction values, due-diligence evidence, contract copies, or pipeline snapshot counts.

## Authoritative system boundaries

| Information object | Authoritative destination | Permitted GitHub representation |
| --- | --- | --- |
| Investment lead, qualification, and related parties | Zoho CRM Leads | Field model, lifecycle contract, validation design |
| Investment opportunity / strategic transaction | Zoho CRM Deals | Conceptual object specification and workflow architecture |
| Investor / capital provider investment mandate | Zoho CRM InvestmentMandates | Domain role and integration contract |
| Acquired/staged investment position, legal holding, financial accounting | Governed investment registers in Google Drive / controlled finance system | Data model and repository-binding policy only |
| Source listings, correspondence, due-diligence evidence, valuations and investment-committee papers | Governed Google Drive evidence folders, linked from CRM records | Evidence manifest specification and access-control rules, without actual evidence payload |
| Integration state, audit events, runtime metrics and operational remediation cases | Authorised operational system / audit store / ticketing system | Instrumentation design and schema, without event instances |

## VS05 logical flow
1. Investment signal and originating thesis.
2. Identity and duplicate check against canonical parties, deals, and source listing identifiers.
3. Lead qualification and conversion to transaction opportunity.
4. InvestCo stage transitions through initial assessment, engagement, valuation, screening, offer, due diligence, investment-committee decision, execution and realisation.
5. Formal holding/transaction registration only when appropriate evidence and authority exist.
6. Portfolio performance, valuation history and value-realisation records remain in governed operational/financial repositories.

## VS boundaries
- VS05 owns investment decisions, portfolio positions and value-realisation governance.
- VS02 owns financing origination, structuring, funding, servicing and finance distribution mechanics; an InvestCo investment position in FinanceCo debt is subject to VS05 investment governance.
- VS01 owns equipment sales/supply and access; VS04 owns productive-asset lifecycle services.
- Funding partners and investment mandate counterparties must not be counted as investee opportunities without a separate, real transaction identity.

## CRM implementation mapping
- Reuse Leads, Deals and InvestmentMandates; do not create a duplicate VS05 module.
- Reuse existing `InvestCo_Stage` S0–S15 semantics.
- `Owning_Value_Stream` and `Governed_Value_Stream` bindings require semantic crosswalk and type validation.
- Provenance attributes such as `Source_URL`, `Source_Platform`, `Source_Listing_ID`, `Listing_Status` are operational **field definitions** only in GitHub; values remain in CRM.
- Use CRM views for operational projections; views are not canonical business records.
- Keep investment committee decisions and authority distinct from approval to publish governed schemas/configuration.
- Use native CRM workflow/Blueprint/approval controls for local state transitions and enforce cross-system policies through approved integration services.

## Repository review controls
- Reject commits containing identifiable deal, lead, funding partner, company-specific holdings, customer/counterparty record snapshots, exported CRM CSV/XLSX files, actual email/correspondence content, source evidence files or asset-level registers.
- Permit architecture decision records, metamodels, schemas, interface specifications, reusable configuration, anonymised fixtures, tests and non-sensitive technical documentation.
- Operational exceptions and evidence belong in controlled business repositories; architectural defects may be documented as GitHub issues **without actual business record payloads**.
- Every architecture change follows governed version control and review; do not interpret this design as an investment/credit decision or production approval.

## Parent authorities
- BA-VS-001 enterprise value stream catalogue (VS05 Investment & Portfolio Value Realisation)
- CAT-ZCRM-CONFIG-001 adopted Zoho CRM configuration object catalogue
- ADR-HUB-FOUNDATION-001 enterprise Hub and authoritative-spoke architecture
- CTL-GOV-CEO-APPROVAL-001 controlled-object approval gate

## Migration note
Legacy operational content accidentally committed to GitHub must be removed from the current tree and relocated to its authoritative application/repository. Git commit and issue-edit histories may retain previous versions and must be assessed separately for repository-history purging, with impact review and authorised administrative action.

## Change-control traceability
The missing change record for the original ADR commit is addressed by
[CHG-20261010-VS05-REPOSITORY-BOUNDARY-LOG](../../agent-workspace/change-log/2026/10/CHG-20261010-VS05-REPOSITORY-BOUNDARY-LOG.yaml).
This corrective record preserves the original CI failure and the ADR's PROPOSED status.
