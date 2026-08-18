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
12. Before every material enterprise system write, apply `CTL-SYS-WRITE-AUDIT-001`: resolve actor, mandate, authority, target, environment and correlation ID; capture or reference the before-state; and use an authorised auditable tool or gateway.
13. After every material enterprise system write, record the result, native transaction/event reference where available, after-state reference, objective evidence and PDCA/task correlation. T2/T3 writes through an unauditable path SHALL fail closed.
14. For every material repository mutation, create or update a same-change-set record under `agent-workspace/change-log/` in accordance with `CTL-DEV-CHG-LOG-001`.
15. Record objective evidence under `evidence/` and/or authoritative Catalyst evidence stores.
16. Update `handoff.md` for the next agent.
17. Perform CHECK/STUDY before recommending closure.
18. Record one ACT decision: ADOPT, ADAPT, REPEAT, REJECT or ESCALATE.
19. Do not treat `DO_COMPLETE` as `TASK_COMPLETE`.

## System-write audit control

- `CTL-SYS-WRITE-AUDIT-001` is the enterprise parent control for auditable writes across enterprise systems.
- Every material write SHALL be attributable to a human, agent, automation, application or integration.
- T2/T3 writes SHALL NOT use a path that cannot produce sufficient audit evidence.
- Audit events are append-only. Corrections create a superseding event; they do not erase history.
- Failed write attempts SHALL be recorded where technically possible.
- Secrets SHALL NOT be written into audit events.
- Native system audit/transaction IDs SHALL be retained when available.

## Change-log control

- `CTL-DEV-CHG-LOG-001` remains mandatory for human, agent and automation changes to KongoniApp repositories.
- Change records are append-only after merge and SHALL NOT be silently rewritten or deleted.
- A protected repository change without a conformant same-change-set log record SHALL fail closed in CI.
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
