# WRK-CAT-MCP-001 — Execution Instruction

## Objective

Deploy and validate `kongoni_mcp_execution_gateway` in Zoho Catalyst `Kongoniapp1` Development.

## Authorised scope

- Development only.
- Use the existing source at `appsail/kongoni_mcp_execution_gateway`.
- Deploy as AppSail with Node.js 20.
- Set `CRM_CONNECTION_LINK_NAME` to the actual link name of the existing `Zoho CRM Write` Catalyst Connection.
- Run read-only CRM validation first.

## Required controls

Before deployment or mutation:

1. Read `agent-workspace/AGENTS.md`.
2. Resolve `KEA-MOD-HS-001` from Catalyst and verify version/hash.
3. Verify `EnvironmentExecutionAuthority` for Kongoniapp1 Development.
4. Verify the active `catalyst-platform-delivery` Agent Contract.
5. Verify the relevant `MCP_Tool_Register` capability is `GATEWAY_REQUIRED` and approved.
6. Record Rule 14 preflight evidence in `MCP_Governance_Log`.

## Deployment

Create or reuse AppSail service `kongoni_mcp_execution_gateway`. Do not create a duplicate. Use Catalyst-managed Node.js 20 runtime and start with `node app.js`.

## Runtime tests

1. `GET /health` returns HTTP 200.
2. A `HARD_BLOCKED` capability returns HOLD/rejection.
3. A valid T2 preflight returns `CONFORMANT` and a preflight ROWID.
4. `/v1/execute` rejects a missing or mismatched preflight.
5. Execute `CRM_ACCOUNT_READ_TEST` only after a valid preflight.
6. Confirm CRM returns 2xx through Catalyst Connections.
7. Confirm no token, secret or Authorization header is returned or logged.

## Stop conditions

Stop and record BLOCKED if Production would be changed, the architecture hash differs, the active Agent Contract cannot be verified, the Connection link name cannot be resolved, or any required control fails.

## Evidence required

Write runtime evidence under `evidence/` and update `handoff.md`. Include AppSail URL, deployment status, architecture hash, preflight ROWID, test results, CRM HTTP status and relevant log result.

## Handoff

After DO evidence exists, hand back to ChatGPT for independent CHECK/STUDY. Do not close the work item.