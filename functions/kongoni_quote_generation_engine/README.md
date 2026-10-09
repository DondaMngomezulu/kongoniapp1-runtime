# AI-Native Quote Generation Engine — ENG-S01-QUOTATION

**Version:** 0.1.0, **Owner:** VS01 Asset Provision & Access, **State:** DEVELOPMENT PROTOTYPE / NOT DEPLOYED / NOT CUSTOMER ISSUABLE.

The existing registered `ENG-S01-QUOTATION` engine is reused. No new Enterprise Engine Catalogue row or competing price engine is introduced. This repository is **public**; commit only synthetic examples and code, no customer quotes, data, secrets, private policy parameters or CRM credentials.

## Responsibility boundary (MECE)

| Stage | Authoritative owner | This engine's responsibility |
| --- | --- | --- |
| Customer intent and candidate product matching | AI-assisted interface; validated against CRM data | Extract *proposed* product IDs/quantities with evidence only |
| Product, configurations, stock | CRM Products and related approved records | Resolve references; does not mint or edit master data |
| Equipment cash pricing | `ENG-S01-DEALER-PRICE` | Consume approved results only |
| Lease/rental and finance pricing | `ENG-S03-LEASE-PRICING`, governed finance engines | Consume approved fixed and per-hour rates only |
| Risk/credit/legal/tax policy | Specialist authoritative systems/approvers | Verify gates and collect evidence; never approve |
| Quotation composition | `ENG-S01-QUOTATION` | Separate one-off, fixed-monthly and planned hourly totals; draft and trace |
| Quote transaction | Zoho CRM Quotes module | Only a *candidate payload* until managed OAuth adapter passes tests |
| Render/merge and distribution | Governed document templates/CRM correspondence | Future adapter; **never done here** |
| Invoice and accounting ledger | Zoho Books | Not owned by this engine |

## What runs now

- `lib/engine.cjs`: deterministic quote draft and versioned evidence manifest; strictly ZAR 2-decimal integer-minor-unit profile.
- `lib/intent.cjs`: injectable approved-model intent interpreter + validation of all AI suggestions (untrusted by design).
- `lib/crm.cjs`: header mapping to verified Quotes fields, with explicit `NOT_WRITE_READY` line-item mapping.
- `index.js`: Catalyst node20 Advanced I/O HTTP adapter for `GET /health`, `POST /preview`. It **never writes CRM**.
- `schema/`: JSON Schema request/response contracts; `agent-workspace/services/SRV-VS01-QUOTE-001/openapi.yaml` records transport intent.
- `test/`: synthetic regression tests runnable without credentials.

## Developer commands

```bash
node --test functions/kongoni_quote_generation_engine/test/*.test.cjs
node --check functions/kongoni_quote_generation_engine/index.js
```

Install dependencies only as part of the approved Catalyst deployment workflow; `zcatalyst-sdk-node` is declared by `package.json` and matches the existing project dependency pattern. No Catalyst instance was deployed by this change.

## Preview API (gated)

Activation requires *all* of `QUOTE_ENGINE_EXECUTION_ENV=Development`, `QUOTE_ENGINE_PREVIEW_ENABLED=true`, and `QUOTE_ENGINE_DEV_USERS=<email allowlist>` configured securely at deployment. Without them, preview returns 503. Catalyst user authentication is checked before any request processing; email outside the allowlist gets 403. In Production the endpoint must remain disabled. Do not attach a public unauthenticated route.

Input wrapper: `{ "quote_request": { ...schema/quote-request.schema.json }, "ai_proposal": null }`. The caller's source snapshot is **never trusted**; the wrapper always supplies `sourceVerified: false`, so release is held. `quote_type` is CASH_SALE, OPERATING_LEASE or DRY_RENTAL. Currency is limited to ZAR. Source tax rate is supplied explicitly as basis points; an example value in tests is not a statutory declaration. Every line uses integer cents, approved source reference, line quantity, separate time basis and tax evidence. A planned hourly forecast is not a minimum usage obligation or an actual invoice.

Output includes `QPREVIEW-<content hash>` (not CRM Quote ID), priced lines, ONE_TIME/FIXED_MONTHLY/HOURLY_VARIABLE/ESTIMATED_MONTHLY subtotals, gate failures, AI review, source provenance, a *non-writeable* CRM header candidate, and `customer_issue_authorised=false`.

## AI-native controls

The LLM is a proposal-only component: it can interpret a customer brief and suggest known product identifiers plus quantities, but cannot change prices, tax, discount, approval, legal classification, template, CRM record or document release. It is wired through `interpretRequirements()` only when an approved model adapter and personal-data-processing approval are supplied. **No live AI provider is currently configured.** Unfamiliar products, mismatched tenants, missing model provenance and price/approval override attempts cause a HOLD. Never send personal/customer information to an unapproved model endpoint.

## Release gates still open

1. Obtain approved AI model/provider, data-processing approval, identity, and tenant boundaries.
2. Implement authoritative CRM read adapter (Deals, Accounts, Products, Prices, Terms, Taxes, template references), readback and effective-date checks. A bare client snapshot is NOT authoritative.
3. Verify Quotes `Quoted_Items` subform API metadata and line mapping, idempotency, error recovery and duplicate suppression. Never infer from a document template.
4. Integrate approved quote rendering and UBL 2.4 profile with actual schema regression and approved source repository.
5. Test CRM dry-run/create/readback and email evidence in a controlled environment; keep all customer issuance blocked until authorised.
6. Resolve the reference standards/APQC process mapping, business owner acceptance, legal review, security controls and production authority.

**Do not merge/deploy/activate by assuming local tests imply CRM or AI production conformance.**
