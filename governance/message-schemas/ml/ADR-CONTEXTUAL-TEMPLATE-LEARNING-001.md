# ADR-CONTEXTUAL-TEMPLATE-LEARNING-001 - AI-native contextual message template intelligence

| Property | Value |
| --- | --- |
| Date | 2026-10-19 |
| Lifecycle | ENGINEERING CANDIDATE / REVIEW ONLY |
| Parent release control | AI-NATIVE-ISSUE-SEND-001, draft PR #70 |
| Governing mail merge | MRG-CVR-001 v1.0, adopted 2026-10-09 |
| Message schema register | ROR-0095, CONTROLLED DRAFT / NOT APPROVED; canonical ID pending |
| Master template register | REG-AGR-TPL-001 |
| CRM authority | Zoho CRM, source of transaction / customer facts, no speculative new fields |
| Document authority | Google Drive governed masters, LibreDocs-compatible ODF for new approved masters |
| Approval and controls | Named Document Controller, commercial/legal/credit approvers, GitHub PR; never autonomous publication |

## Decision requested

Establish a contextual, supervised, review-only learning capability that (A) recommends among *independently confirmed approved* customer message templates, (B) discovers recurrent quality problems in governed drafts, and (C) identifies missing template patterns. Reuse stable enterprise IDs and do not let model output approve, publish, amend, sign or send anything. No CRM, LibreDocs or communication-channel deployment is authorised by this engineering draft.

This candidate architecture extends existing enterprise message/document governance instead of creating a competing template repository. Models must not override eligibility, policy, source currency, validated pricing, required attachments, typed merge data, account status, permitted channel or recipient identity.

## Logical architecture

1. **Trusted context extractor (CRM side):** derive controlled categorical fields from the active record, e.g. `value_stream`, `intent`, `document_class`, `channel`, `issuer_entity`, `stage`, `contract_type`, `audience`, `locale`, `available_fields`. Canonical classification comes from approved business rules. Use the enterprise dictionary/Genericode values; strings in the prototype are placeholders for the mapped codes, not authority to mint codes. Do not hand unfiltered customer text to training by default.
2. **Authoritative snapshot resolver:** read the actual canonical template register and source master, approval state, binding mapping, exact template revision/content digest and compatible parent business-document template. This layer MUST independently authenticate the snapshot. The current message register has pending canonical identity and runtime validation, so production eligibility remains unverified.
3. **Hard deterministic eligibility:** exclude draft, retired, HOLD, missing approval evidence, mismatched issuer, value stream, message purpose, document class, permitted channel, stage, contract type and locale. A model score cannot rescue a blocked template. If a class-appropriate template exists but is held, report `GOVERNANCE_HOLD` rather than spuriously suggesting another template. Missing required fields yields `MISSING_SOURCE_BINDINGS`, not a new-template request.
4. **Supervised ranking:** train a pairwise linear context-to-template ranker on independently validated human-review selections versus *other templates shown at the same decision*. The prototype uses feature crosses between controlled context values and approved template IDs plus soft audience preference. The output is a ranking score, **not a calibrated probability** and never a release decision. A cold-start, unverified registry or low-margin situation produces ABSTAIN. Future approved versions may use embedding search over approved template summaries (within the hard-filtered set) and a gradient-boosted learning-to-rank model after sufficient labelled observations.
5. **AI candidate composition:** AI may suggest a style-appropriate message and missing field list using the selected version-pinned master only. Parent document clauses and quote economics remain deterministic and controlled. The published ODF/PDF or HTML variant is rendered and checked by the established document-generation process.
6. **Review & feedback:** authorised reviewer marks correct/incorrect selection and structured reason. Capture `ACCEPTED`, the exact alternatives shown, relevant intent classification, a proof of reviewer authority, and the model/template/snapshot versions. Store no message body, personal contact details, banking identifiers, commercial prices or customer names in the learning dataset by default. Conversion rate and click/open rate are **not** correctness labels. Do not learn from unreviewed AI draft decisions or stale template versions.
7. **Novelty/change-mining:** aggregate verified `NO_APPROVED_SEMANTIC_TEMPLATE` or `REPEATED_REVIEW_EDIT` signals. An engineering trial threshold is at least **three distinct pseudonymous transactions** with a common context; this is a review-queue threshold, not a production policy. Before a new master is proposed, search all template lifecycle states including DRAFT and HOLD to prevent duplicates. Repeated modifications to an existing master create a *revision* proposal instead.
8. **Human template governance:** every proposed candidate must pass semantic ownership/deduplication, source precedent and legal/commercial review, corporate HTML/ODF typesetting validation, required merge-field crosswalk, version/hash, UBL profile applicability, security/privacy, and explicit register approval. New canonical IDs require approved SCOPE-002 authority. Publish to Drive/CRM only after approved change and readback; never auto-register from the model.
9. **Separate authorised release:** the downstream `AI-NATIVE-ISSUE-SEND-001` control rechecks exact live facts, approval evidence, recipient, attachments, idempotency and channel permissions immediately before transport. ML is neither a policy-decision point nor a send executor.

### Nomatiki finance-lease example (reasoning illustration, NOT a live training record)

A `VS02` customer enquiry for road-construction equipment with proposed `FINANCE_LEASE` structure is initially a draft/budgetary case if supplier purchase prices, mandatory equipment matching, credit release or active template publication are missing. The classifier must not relabel a budgetary proposal as a formally approved quote just because historical users often issued quotes. Candidate selection must preserve `VS02-04 Budgetary Proposal` (CRM email template `5643538000009741001`) as a separate scenario from a formal quotation. The actual crosswalk currently marks that template `HOLD_AUTOMATED_SEND`. Similarly, the `OASIS UBL 2.5 - Quotation` CRM template `5643538000008802024` is active in CRM but crosswalk publication/validation is not established. No customer send is authorised.

## Data contracts, provenance and boundaries

- **Inference context:** strict allowlisted categorical features; no customer email, telephone, credit figures, banking information or free-text CRM notes. Derived categories require recorded source field/ID and taxonomy version in the trusted source snapshot, not in the ML feature payload.
- **Training event:** context, alternatives actually shown, accepted choice, reviewer-verification, approved learning use. Reviewer identity and independently verified signed/authoritative receipt are held in the secure evidence store; an untrusted JSON Boolean is not an approval. The sample Python function requires an out-of-band trusted receipt flag but **does not** verify signatures.
- **Catalogue snapshot:** retain authoritative register URI, exact template ID/version/status/master SHA-256, issuer scope, message class, channels, stage and required field bindings. Model code only checks field formats; trusted services must authenticate contents and publication state.
- **Gap signal:** context plus coded reason and distinct HMAC-pseudonymous case token; avoid raw text, deal IDs and low-count individual profiling. The prototype requires a 64-character token but cannot verify that the token was generated using a protected HMAC key.
- **Model artifact:** feature contract version, source/train cutoff, schema and code revision, training sample counts, approval state, quality metrics, drift baseline and SHA-256, retained by authorised model registry after separate governance. Never store production private training rows in public GitHub.
- **Privacy and information governance:** assess purpose limitation, lawfulness, retention, access control and downstream model-vendor processing before using customer-derived data. POPIA sections 13-15 apply to purpose, retention and compatibility of further processing. Use privacy/data-protection review prior to training and avoid collecting more data than needed.

## Learning strategy

| Stage | Approach | Admission gate |
| --- | --- | --- |
| 0 - Cold start | Rule-only eligibility; suggest if one candidate, otherwise human select/ABSTAIN | Verified registry/authority first |
| 1 - Pilot | Supervised pairwise linear ranker on human reviewed choices; model remains review-only | Sufficient independent labels and offline evaluation |
| 2 - Discovery | Coded correction analysis + distinct-case gap detection; duplicate checks | Human-confirmed signals and template register sweep |
| 3 - Advanced | Embeddings of non-sensitive **approved template summaries** and a calibrated learning-to-rank challenger | Privacy review, dataset sufficiency, measured incremental benefit |
| 4 - Deployment | Inference through authenticated adapter; model cannot access sending credentials | Governance, independent source verification and tested downstream issue/send control |

### Proposed evaluation gates (targets; not achieved results)

- Out-of-time and distinct-account grouped validation; no shared transactions across train and test. Retain negative examples of nearly identical but wrong contract type, issuing entity, channel, or approval status.
- For a reviewer-selected approved template, aim for top-1 correctness >= 90% and recall@3 >= 98% on a representative labelled holdout. Compare against rules-only and most-common-template baselines and report bootstrap uncertainty.
- **Zero** blocked-template recommendations, incorrect legal-entity matches, wrong business-document class, missing parent-document bypass, or unapproved model-triggered publication in adversarial tests.
- Report coverage, no-match frequency, abstention and appropriate abstentions separately; high overall accuracy with low usable coverage is insufficient.
- Track accepted-first-draft rate, substantive manual edits, unresolved merge fields, reviewer override reasons, duplication avoidance and control exceptions. Ignore commercial conversion as a proxy for legal/content accuracy.
- Slice by VS01/VS02/VS03/VS04/VS05/VS06, equipment offering, document class, stage, sender entity, channel and language; fail promotion on material regression, even if aggregate accuracy improves.
- Model replacement requires documented experiment, reproducible input cutoff, independent test, model card, approval, canary, rollback and audit. Retraining cadence must be justified by volume/drift, not invented as an always-on process.

## Implementation interfaces and release boundaries

| Component | Proposed owner / runtime | Action |
| --- | --- | --- |
| Policy and semantic code lists | Enterprise Dictionary, Genericode, source registers | Define allowed classes, purpose, status, channels and relationship semantics |
| Context extraction | Native Zoho CRM Functions / Deluge | Produce evidenced categorical context from active CRM transaction |
| Training/ranker | Offline trusted Python worker or approved model runtime | Fit on authorised curated labels, return review-only scores |
| Model monitoring and review | Enterprise Architecture / Data Steward | Compare drift, release/change register, red-team and evaluation |
| Template master rendering | Authorised LibreDocs/ODF adapter and Google Drive | Assemble/render only on existing approved template master; ODF/PDF fidelity proof |
| Document Controller | REG-AGR-TPL-001 / MRG-CVR-001 | Approve new/revised message or document template and exact hashes |
| Customer send | `AI-NATIVE-ISSUE-SEND-001` controlled CRM dispatch gateway | Independent fail-closed release action, not driven by model label |

No Zoho CRM field additions should be inferred from these conceptual properties: CHG-TS-CRM-001 (issue #135) requires its own explicit CEO approval and existing-field reuse. No model service, test dataset, registration status, permissions, customer message, or production business document is updated by this change.

## Required review decisions and follow-ups

1. Document Controller to approve the exact authorised source catalogue snapshot, ownership and permissible feedback labels; crosswalk with the adopted `MRG-CVR-001` source and corporate format profile.
2. Data Steward and privacy officer to approve feature whitelist, model data purpose/retention and signed human-feedback receipt. Training on real interactions remains blocked pending this evidence.
3. Enterprise Architecture to adopt the feature contract and its relationship to `AI-NATIVE-ISSUE-SEND-001` in SysML, with GitHub PR and regression tests.
4. CRM Architecture to implement Deluge context extraction without adding speculative fields, and ensure no send permissions in the ML service.
5. Pilot with representative anonymised labelled decisions and compare against deterministic eligibility; keep assisted suggestions human-reviewed.
6. Allocate controlled identity through SCOPE-002 and register any actual template revision/new master separately under REG-AGR-TPL-001 only after full review and readback.

## Supporting external reference material (not automatic enterprise adoption)

- NIST AI RMF 1.0 and Generative AI Profile (NIST AI 600-1): https://www.nist.gov/itl/ai-risk-management-framework and https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- South African POPIA, Act 4 of 2013: https://www.justice.gov.za/legislation/acts/2013-004.pdf
- ICO guidance on data minimisation in supervised machine learning (comparative): https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/how-should-we-assess-security-and-data-minimisation-in-ai