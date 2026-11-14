# AGENTS.md — Kongoni Governed Agent Collaboration Protocol

All agents working in this directory SHALL follow this protocol before execution.

1. Read this file.
2. Read the assigned `mandate.yaml`.
3. Resolve the active architecture from Zoho Catalyst.
4. Verify architecture ID, version, active state and content hash.
5. Read `instruction.md`, `plan.yaml` and the latest `handoff.md`.
6. Resolve the executing Agent Contract in Catalyst.
7. Resolve `EnvironmentExecutionAuthority` for the target platform and environment.
8. Resolve the requested capability in `MCP_Tool_Register`.
9. For T2/T3 system changes, complete Rule 14 architecture preflight before any mutation.
10. Respect `GATEWAY_REQUIRED` and `HARD_BLOCKED` controls.
11. Execute only the authorised scope.
12. For every material repository mutation, create or update a same-change-set record under `agent-workspace/change-log/` in accordance with `CTL-DEV-CHG-LOG-001`. The record SHALL identify the actor, mandate, task class, authority, affected paths, intended outcome, PDCA state and evidence.
13. Record objective evidence under `evidence/` and/or authoritative Catalyst evidence stores.
14. Update `handoff.md` for the next agent.
15. Perform CHECK/STUDY before recommending closure.
16. Record one ACT decision: ADOPT, ADAPT, REPEAT, REJECT or ESCALATE.
17. Do not treat `DO_COMPLETE` as `TASK_COMPLETE`.

## P0 governed external issue and send — AI-NATIVE-ISSUE-SEND-001

- **No direct AI egress:** Every agent SHALL treat CRM native `sendMail`, Gmail send, mass mail, workflow emails, WhatsApp, WeChat, e-signature issue, outward document publication and externally shared document links as governed **ISSUE/SEND** actions. Holding an administrator or human OAuth token is not an authorisation to transmit.
- **Resolve template before composition:** Use the approved, current template/message profile or a specifically approved immutable one-off instance. Bind CRM transaction, legal issuer, business intent, message/body and document template versions, channel, sender identity, To/CC/BCC audience, subject, rendered artifacts, attachment hashes and delegated approval. Unknown or HOLD means **DENY**.
- **Enforce exact release:** Only a trusted, independently authenticated, CRM-owned issue/send dispatcher can reserve one idempotency key and issue the exact approved payload. Draft validation, a signed-looking field, repository test result or an AI's asserted approval shall never be treated as an egress capability.
- **Current P0 condition:** The designated CRM sandbox was last recorded as refreshed on 17 August 2026, and the direct-send routes and agent-specific effective permissions remain unverified. **Until a production gateway and all provider routes are verified and approved, AI agents SHALL draft only and SHALL NOT send customer-facing messages or publish governed documents on their own.** A user's instruction to send does not implicitly waive these technical controls.
- **Exceptions:** Register an exact approved transaction-scoped template instance through the existing governance and delegated approval process. An agent cannot approve its own exception. Human break-glass remains separate, explicitly approved, scoped and auditable; it does not confer rights on AI identities.
- **Work-product disposition:** Mark preview or internal review materials `REVIEW_ONLY`; never mark a proposed instance `ISSUED` or `DELIVERED` without a CRM-authoritative transport receipt. Retain operational business records and approvals in CRM, templates and source documents in their authorised repositories; commit only sanitized configuration metadata and synthetic tests to GitHub.
- **Architecture trace:** Implement against GitHub configuration twin and CI before sandbox and production, per [P0 Issue #67](https://github.com/DondaMngomezulu/kongoniapp1-runtime/issues/67) and [draft PR #70](https://github.com/DondaMngomezulu/kongoniapp1-runtime/pull/70). This agent protocol provides a procedural stopgap, not proof of provider-level enforcement.

## Change-log control

- `CTL-DEV-CHG-LOG-001` is mandatory for human, agent and automation changes to KongoniApp.
- Change records are append-only after merge and SHALL NOT be silently rewritten or deleted.
- A protected change without a conformant same-change-set log record SHALL fail closed in CI.
- T2/T3 work SHALL NOT set `task_complete: true` without objective CHECK/STUDY evidence and a valid ACT decision.
- Secrets SHALL NOT be written to the change log.

## Authority rules

- A coordinator does not inherit execution authority.
- Agents SHALL NOT self-approve reserved decisions.
- Production changes require their own active authority and approval.
- Missing, stale, ambiguous or non-conformant architecture data SHALL fail closed.
- Credentials, access tokens, refresh tokens, passwords and secrets SHALL NOT be committed to GitHub.

## Collaboration rule

Agents collaborate by updating governed work objects. Chat messages are not the authoritative work state.
