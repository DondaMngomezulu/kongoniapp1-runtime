# AGENTS.md — Kongoni Governed Agent Collaboration Protocol

All agents working in this directory SHALL follow this protocol before execution.

1. Read this file.
2. Read `governance/agent-workspace-authority-boundary-v0.1.yaml`.
3. Read the assigned `mandate.yaml`.
4. Resolve the active architecture from its designated authoritative source; where the architecture is designated authoritative in Zoho Catalyst, resolve it from Catalyst.
5. Verify architecture ID, version, active state and content hash.
6. Read `instruction.md`, `plan.yaml` and the latest `handoff.md`.
7. Resolve the executing Agent Contract in Catalyst where applicable.
8. Resolve `EnvironmentExecutionAuthority` for the target platform and environment.
9. Resolve the requested capability in `MCP_Tool_Register`.
10. For T2/T3 system changes, complete Rule 14 architecture preflight before any mutation.
11. Respect `GATEWAY_REQUIRED` and `HARD_BLOCKED` controls.
12. Execute only the authorised scope.
13. For every material repository mutation, create or update a same-change-set record under `agent-workspace/change-log/` in accordance with `CTL-DEV-CHG-LOG-001`.
14. Record objective evidence under `evidence/` and/or reference the designated authoritative evidence locus.
15. Update `handoff.md` for the next agent when required.
16. Perform CHECK/STUDY before recommending closure.
17. Record one ACT decision: ADOPT, ADAPT, REPEAT, REJECT or ESCALATE.
18. Do not treat `DO_COMPLETE` as `TASK_COMPLETE`.

## Authority rules

- `agent-workspace` is an engineering execution/evidence workspace, not an enterprise system of record.
- A file located under `agent-workspace` does not become authoritative merely because it is validated, version-controlled or used by an agent.
- A validator establishes conformance only; it does not establish business, legal, accounting, tax or commercial authority.
- Governed Catalogues, Libraries, Registers and Matrices retain the authority assigned to them by their adopted governance record.
- External normative sources retain their own authority. Machine-readable representations, crosswalks and schemas are controlled representations only unless explicitly designated otherwise.
- GitHub is the governed engineering repository for engineering artifacts and their change history.
- Zoho Catalyst may be the authoritative source for designated runtime, execution-control and architecture records; this designation is object-specific, not a blanket authority over all enterprise records.
- A coordinator does not inherit execution authority.
- Agents SHALL NOT self-approve reserved decisions.
- Production changes require their own active authority and approval.
- Missing, stale, ambiguous or non-conformant authority data SHALL fail closed.
- Credentials, access tokens, refresh tokens, passwords and secrets SHALL NOT be committed to GitHub.

## Change-log control

- `CTL-DEV-CHG-LOG-001` is mandatory for human, agent and automation changes to KongoniApp.
- Change records are append-only after merge and SHALL NOT be silently rewritten or deleted.
- A protected change without a conformant same-change-set log record SHALL fail closed in CI.
- T2/T3 work SHALL NOT set `task_complete: true` without objective CHECK/STUDY evidence and a valid ACT decision.
- Secrets SHALL NOT be written to the change log.

## Collaboration rule

Agents collaborate by updating governed engineering work objects and by referencing authoritative enterprise objects. Chat messages are not the authoritative work state.