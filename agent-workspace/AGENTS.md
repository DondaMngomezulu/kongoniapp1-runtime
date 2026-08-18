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
12. Record objective evidence under `evidence/` and/or authoritative Catalyst evidence stores.
13. Update `handoff.md` for the next agent.
14. Perform CHECK/STUDY before recommending closure.
15. Record one ACT decision: ADOPT, ADAPT, REPEAT, REJECT or ESCALATE.
16. Do not treat `DO_COMPLETE` as `TASK_COMPLETE`.

## Authority rules

- A coordinator does not inherit execution authority.
- Agents SHALL NOT self-approve reserved decisions.
- Production changes require their own active authority and approval.
- Missing, stale, ambiguous or non-conformant architecture data SHALL fail closed.
- Credentials, access tokens, refresh tokens, passwords and secrets SHALL NOT be committed to GitHub.

## Collaboration rule

Agents collaborate by updating governed work objects. Chat messages are not the authoritative work state.