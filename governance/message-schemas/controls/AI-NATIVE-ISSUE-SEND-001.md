# AI-NATIVE-ISSUE-SEND-001 — Controlled Customer Message and Business Document Release

**Proposed implementation** | 19 October 2026 | **REVIEW ONLY; not deployed or approved for production**

## Authority and existing controls
- CEO direction of 19 October 2026 requires governed templates for **all** external customer correspondence, and governed parent business documents whenever applicable.
- Preserve **MRG-CVR-001 v1.0** CEO-adopted covering-email merge scheme, shared footer **TPL-KNG-CVR-FOOTER-001**, existing template and CRM IDs and source status.
- Enterprise Message Schema Register (Drive, ROR-0095) remains **CONTROLLED DRAFT / NOT APPROVED** with a canonical ID pending. GitHub stores engineering projections only.
- Corporate presentation profile is currently candidate; this policy never upgrades its status.
- Continue open change issues #52 and #54; the document master **VS02-DOC-004** is FOR CONFIGURATION AND APPROVAL.
- **No new CRM fields or production mutations** are authorised by this PR. Apply the user's Group CEO approval to engineering preparation and tests only; production promotion is a separate gate.

## Invariant
A release action (ISSUE, SEND, SIGN, PUBLISH_EXTERNALLY) MUST NOT execute unless a trusted synchronous validator returns ALLOW for the **exact immutable snapshot**, identity, recipient(s), channel, document(s), authorization and one-time idempotency key immediately before the transport call. A draft is never permission to send.

## Scope
EMAIL / WHATSAPP / WECHAT / OTHER APPROVED EXTERNAL CHANNELS. Applies to enquiry, quotation, pro forma, budgetary proposal, finance lease, operating lease, sales order, invoice, receipt, agreement, renewal, notice, customer clarification, warranty, delivery, debt collection, payment request and supporting covering correspondence. Classify the message from the business intent; do not substitute a superficially similar schema.

## Source-of-truth boundaries
1. Google Drive: governed template and business-document masters and exact source revisions. LibreDocs-compatible ODF masters for new governed documents when authoring connection is verified.
2. CRM: customer/transaction identity, fields, line items, communication record, permitted sender, owner, agreement, issuance state, source evidence and secured issue/send function.
3. GitHub: proposed enterprise architecture, SysML, deterministic policy functions, schemas, test evidence, code review. Never use source-control code as proof of the canonical approval state.
4. Document Controller/approval register: publication, lifecycle, version, immutable hashes and explicit authoriser identity.
5. AI models: classify, suggest template and compose candidate text; NEVER authorise publication, set PASS, write release evidence, obtain credentials or invoke unapproved delivery channels.
6. Trusted native CRM Deluge dispatch gateway: decision and transport in one guarded operation; re-read current source and approval state. External transports only via approved, least-privileged adapters.

## Protocol (canonical candidate keys, not new CRM fields)
1. REQUEST: bind customer account, contact(s), issuing legal entity, value stream, business class, channel, record, and requested action.
2. RESOLVE: fetch **unique exact** approved template ID/version/hash with compatible channel, issuing party and transaction class. Reject ambiguous candidates, missing approval evidence and template HOLD.
3. ENRICH: snapshot CRM field values, related pricing/quote/service records, schema/version, template hash, documented parent business-document ID/version/hash and line items. Do not guess unknown values. Attach source receipts.
4. COMPOSE: AI creates a candidate from approved immutable template; natural-language content is treated as untrusted input to validation. Resolve every required merge parameter and standard corporate footer. Reject unresolved macros and free-form replacement of operative clauses.
5. RENDER: produce approved editable document/HTML/PDF as applicable, test actual artifact and hash. If parent business document is required, require a published/unheld parent master, a validated *rendered instance*, contract semantic profile and exact attachment content hash.
6. VALIDATE: synchronous deterministic gate checks exact template, trusted separate evidence, source dates, matching issuing legal entity, recipients, consent/permissions, approved price/rule/version, mandated delivery evidence, finance underwriting conditions, no null required fields, regulatory clauses, correct amounts/currency/VAT, and required approvals.
7. AUTHORISE: independent delegated role and signer approves exact source/render hashes, recipient set, channel and expiry. Ordinary AI-authored assertions are NOT trusted approval.
8. ISSUE/SEND: trusted dispatcher re-reads authoritative sources, recomputes equality with approved digests, atomically reserves the idempotency key and calls only an authorised transport. No separate prior-only 'preflight PASS' is adequate.
9. AUDIT: retain signed/authoritative receipt, decision, version hashes, user/service identity, channel, parent document, recipients reference, timestamp, transport result and correlation ID. Do not log sensitive raw body or secrets unnecessarily.
10. CHANGE: any field/recipient/template/document/price/approval modification invalidates previous approval; force fresh review.

## Fail-closed policy
Deny absent/stale template, absent immutable approval receipt, conflicted registered identifiers, mismatched business-document class, missing parent, mismatched title/version, unverified account, missing equipment specifications/price, revoked sender, missing mandatory availability, missing credit/funding approval, expired quote, unsecured attachment, forbidden endpoint, reused idempotency key, missing evidence or source race.

## Constraints and threat model
- A CRM workflow custom function can be asynchronous and CANNOT guarantee veto of send. Do not use post-send workflow as guard.
- An ordinary CRM `active` template and even an 'approved' folder label do not prove publication.
- Native CRM manual Send Email, Gmail, Zoho Writer/LibreDocs direct exports, mobile WhatsApp, third-party integrations, webhooks, API clients, import, bulk jobs and admin override must have explicit restriction/monitoring controls. Do not claim enterprise-wide enforcement until channel/permission-level bypass testing proves it.
- Enforce separation of duties: author/AI cannot create trustworthy source or approval receipts.
- Policy exceptions require independently approved, named, scoped, expiry-bound record. No free-form emergency override; cannot waive statutory prohibitions.
- Positive validation on independently provided signed/trusted context only. The JSON contract validator in this PR is engineering preflight, NOT a production signature verifier, content renderer, CRM transaction, or transport handler.

## Operational acceptance
A. Allow an exactly matched approved customer message with verified parent and recipient through controlled dispatch only.
B. Negative tests: missing template, pending approval, wrong channel, template/master hash tamper, wrong party, no parent document, missing merge field, finance credit HOLD, stale CRM snapshot, unauthorized sender, duplicate request, and transport bypass.
C. Verify actual permission removal/bypass resistance for native UI, API, Gmail and WhatsApp; prove reject events persisted.
D. Produce rollback, approver reference, deployment version, test receipt, reviewer approval and independent production readback.
E. Before configuration, validate the 19 Oct CRM issue #135 constraints: reuse existing fields, preserve group CEO field-change gate, implement no speculative schema additions.
F. Nomatiki record 5643538000005574006 must remain NOT ISSUABLE while Can_Issue_Quotes=false and Master_Data_Status=PENDING RECONCILIATION.

## Named handovers
Document Controller: signed registry status/merge-field and parent master validation. CRM Architecture: exact field crosswalk, synchronous Deluge service + permissions and CRM tests. Enterprise Architecture: SysML projection and code review. Security: audit, token capability, bypass protection. Business Owner: commercial and credit policies and release criteria.

**Change classification:** engineering REVIEW ONLY. No claim that customer correspondence is technically blocked enterprise-wide yet.

## Stronger enterprise control amendment — 20 October 2026 (review candidate)
**Root-cause case:** Constructo's underwriting email was sent through Zoho CRM as ad hoc HTML without a verified governed template instance. CRM send permission did not synchronously require template resolution. The later finance term sheet remained a review draft, but no production-quality template binding or source/proof reconciliation was evidenced. Treat as CONTROL FAILURE requiring prevention, not a new policy family.

### Mandatory binary decision
- Every AI-originated external message must use **either** (A) a governed, currently approved message template compatible with business intent, legal issuer, channel and receiver class, **or** (B) a **specifically approved immutable template instance**, tied to exact text hash, template hash, issuing entity, CRM record, recipient set, channel, business purpose, approval receipt and expiry. An agent may request B but cannot grant it.
- Every governed business document, including an indicative term sheet, must resolve an approved document class, exact published or specifically approved template, source facts, calculations and version/hash. A covering message does not replace its governed parent. Where a document is only a draft, sharing externally requires explicit document-specific authority, never implicit send rights.
- All outbound business correspondence (including apparently routine information requests) must pass this gate. **Credit approval is not mandatory for an accurately labelled underwriting information request**, but is mandatory where operative credit/funding terms or an executable offer are represented. Distinguish DRAFT / INDICATIVE / ISSUED / COMMITTED.
- A general executive instruction to 'send' does not waive approval of the exact template. Unknown status means DENY and create a short exception request. An approved specifically composed text is treated as a registered immutable one-off **template instance**, not a standing master or a blanket free-form exemption.
- Scope of the signed release receipt includes action, business-intent identifier, issuer, sender/service account, CRM transaction, original template and master hashes, exact rendered email/body and attachment hashes, resolved source snapshot, recipient set, channel, classification and expiry. Any change revokes release.
- Human users and AI agents must have distinct delivery identities, and general agent tokens must not hold direct Zoho CRM Send Mail, Gmail send, provider chat send, mass mail or external publish rights. Where underlying APIs cannot be denied selectively, enforce through identity/role restriction and a least-privileged synchronous CRM-owned dispatcher; retain protected manual break-glass under recorded human approval.
- The dispatcher must atomically authorise and send the exact approved payload with one-time idempotency reservation. Blueprint/workflow post-processing and after-the-fact monitors cannot replace a synchronous send veto.
- Coverage must include CRM record and native Send Mail, workflow functions, mass/bulk mail, third-party APIs, direct Gmail, channel apps, Zapier-equivalent adapters, document-export share links, document attachments and agent tool connectors. Prove each bypass closed via role/provider configuration and negative live Development tests before Production.

### Release-receipt and test controls
The review JSON Schema and preflight now require explicit intent, issuance basis, immutable message digest, approved recipient/channel/action/CRM/template scope, and exact parent document instance hash for document-bound messages. A specific-template approval is scoped to exact audience/content/issuer/purpose/version/expiry, independently authenticated by the actual release service. The review preflight deliberately returns **REVIEW_ONLY** on nominal inputs; no one may interpret that as ALLOW.

Regression must include: ordinary underwriting request without credit decision; attempt to send a finance lease offer despite credit HOLD; approved one-off message with same text and recipients; altered recipient; altered content hash; template replaced after approval; revoked signer; stale CRM data; approval expired; missing parent/attachment; inactive profile; mobile/provider direct send; direct CRM sendMail; duplicate retry; revoked agent permissions. Policy must not block harmless internal drafts or human-to-human chat outside governed enterprise channels, but no externally issued governed record may bypass.

### Existing work and ownership
Extend this PR and [#67](https://github.com/DondaMngomezulu/kongoniapp1-runtime/issues/67), not a new register. Reuse adopted MRG-CVR-001, REG-AGR-TPL-001, REG-KNG-BDT-001, ROR-0095, [PR #68](https://github.com/DondaMngomezulu/kongoniapp1-runtime/pull/68), [PR #12](https://github.com/DondaMngomezulu/kongoniapp1-runtime/pull/12), and authoring/identity [#60](https://github.com/DondaMngomezulu/bug-free-octo-journey/pull/60) / [#62](https://github.com/DondaMngomezulu/bug-free-octo-journey/pull/62). Jane/Document Control handles status and lineage, Reandra coordinates accountable approvals and exceptions, CRM Application Owner implements controlled send, Security restricts channel grants, Architecture governs SysML and interoperability.

**HOLD FOR PRODUCTION:** CRM direct transport permissions, trustworthy signed release evidence, exact live field/API mapping, ODF rendering, canonical ID allocation, test gateway integration, independent functional/security tests, rollback and CEO ACT remain unresolved.
