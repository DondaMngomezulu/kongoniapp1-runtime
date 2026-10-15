# CHECK/STUDY - Universal message release gate synthetic test report

**As-of:** 2026-10-15 UTC. **PR:** [#68](https://github.com/DondaMngomezulu/kongoniapp1-runtime/pull/68). **Task:** [#67](https://github.com/DondaMngomezulu/kongoniapp1-runtime/issues/67).
**State:** **RELEASE HOLD / NOT DEPLOYED**. Tests use synthetic fixtures only; no customer communications were sent by the test.

## 1. GitHub Actions readback (original PR head `d0bbaa6592eeff3a8fe3406f5afc30734121850b`)

- [Candidate Outbound Message Release Gate](https://github.com/DondaMngomezulu/kongoniapp1-runtime/actions/runs/38783629196): **SUCCESS**. Logs state `PASS: 1 synthetic candidate, 22 negative semantic cases, 12 required-field negatives, 2 missing trusted register cases.` This proves the bounded candidate policy's fixtures executed, not payload-schema conformance or interception of any real sender.
- [KongoniApp Change Log Control](https://github.com/DondaMngomezulu/kongoniapp1-runtime/actions/runs/38783628625): **FAILED**, log says `protected repository changes require a same-change-set change-log entry`. Remedy: include a schema-valid change-log file in the PR, then confirm a new run.

## 2. Local adversarial decision-logic evaluation (independent synthetic harness)

A local test reproduced the candidate's decision branches and compact structural guards and altered one field of its approved **synthetic** fixture at a time. The test is **not** an external normative-XSD check and does not exercise live CRM/provider adapters.

All **9/9 manipulated candidates** returned `ALLOW_CANDIDATE_ONLY` despite at least one changed reference requiring independent validation:

| Negative variation | Candidate decision | Missing verification |
| --- | --- | --- |
| Unregistered template ID | ALLOW_CANDIDATE_ONLY | Template registry membership/version/status |
| Insurance-claim message type bound to OASIS reminder fixture | ALLOW_CANDIDATE_ONLY | Message-type-to-standard/profile applicability |
| Arbitrary approval evidence reference | ALLOW_CANDIDATE_ONLY | Authoritative approval event and actor |
| Arbitrary validation evidence reference | ALLOW_CANDIDATE_ONLY | Trusted validation engine attestation/payload binding |
| Unknown channel rendering ID | ALLOW_CANDIDATE_ONLY | Registered channel rendering binding |
| Unknown delivery adapter ID | ALLOW_CANDIDATE_ONLY | Approved adapter binding |
| Unknown issuing-entity ID | ALLOW_CANDIDATE_ONLY | Canonical entity/issuer resolution |
| Substituted syntactically valid SHA-256 digest | ALLOW_CANDIDATE_ONLY | Actual payload hashing and signature/receipt |
| Arbitrary audit-record reference | ALLOW_CANDIDATE_ONLY | Verified append-only audit persistence |

These results demonstrate **missing checks in this candidate function**, not that any production message was sent or that every false evidence assertion would pass a future trusted upstream component. `ALLOW_CANDIDATE_ONLY` is *not* a send permission.

## 3. Live CRM configuration readback (read-only)

- `CustomerCommunications` exposes **74 fields**, including message profile, template, channel, approval and audit-related fields.
- `getValidationRules(CustomerCommunications)` returned **204 / no rules**.
- `getBlueprint(CustomerCommunications)` returned **204 / no blueprints**.
- `getEmailTemplates(CustomerCommunications)` returned **2 active templates**.
- Direct CRM send mail APIs remain a potential routing bypass because no authenticated message-schema interceptor was confirmed for them. **No test email was sent.**

## 4. Required remediation before approval or production

1. Keep the message-register approval gate open (existing ROR-0095; governed identity not yet approved). Bind messageType, exact standard/version/artifact, template and channel jointly to an independently trusted register snapshot.
2. The evaluator must take trusted, versioned **template/channel/issuer** registries and verified approval, validation, receipt and audit evidence; reject missing/revoked/nonmatching entries, even when a message supplies `true` flags.
3. Verify that the reported SHA-256 digest matches the immutable payload and the validation evidence is bound to that same digest; execute exact relevant normative XML XSD / OpenAPI / JSON Schema and business rules.
4. Build simulated direct-API, provider, agent, UI, mass-mail and retry/idempotency bypass-negative tests in **Development only**; deny send when gate unavailable.
5. Produce CI evidence, independently reviewed CHECK/STUDY, ACT approval and live deployment readback, with no customer data or secrets in GitHub.
6. Retest the change-log governance workflow after adding a same-change-set entry; do not treat one green test as production readiness.

**CHECK/STUDY result:** candidate schema/negative-fixture tests PASS; end-to-end runtime and authority tests NOT VERIFIED; secure release acceptance **FAIL / HOLD**.
