# kongoni_mcp_execution_gateway

Cloud-first AppSail runtime for Kongoniapp1 MCP mutation governance.

## Purpose

This service enforces the Rule 14 architecture read-before-change control before material MCP operations. It is bound to `KEA-MOD-HS-001` v0.1 and the active Kongoniapp1 Development execution-authority model.

## Endpoints

- `GET /health`
- `POST /v1/preflight`
- `POST /v1/execute`

`/v1/execute` is deliberately allow-list based. The initial implemented downstream operation is `CRM_ACCOUNT_READ_TEST`; arbitrary URLs, methods, credentials and authorization headers are not accepted.

## Required environment variable

`CRM_CONNECTION_LINK_NAME` = actual Catalyst Connection link name for the configured `Zoho CRM Write` connection.

## Deployment target

- Project: Kongoniapp1
- Project ID: 86824000000020001
- Environment: Development only
- Runtime: AppSail, Catalyst-managed Node.js 20
- Startup command: `node app.js`

## Governance

The runtime must fail closed when the active architecture cannot be resolved or its version/hash differs from:

- Architecture: `KEA-MOD-HS-001`
- Version: `0.1`
- SHA-256: `e989c6a984b9ef3d1bcca02e31ceda8b50687124d7cb40c5957c40864f1c7526`

Material operations require a valid preflight evidence record in `MCP_Governance_Log`. Existing `HARD_BLOCKED` capabilities remain prohibited.

## Deployment handoff

The current Zoho Catalyst MCP management surface can list AppSail services but does not expose first-time AppSail creation/deployment. The remaining bootstrap is therefore: deploy this folder to AppSail in Kongoniapp1 Development, set `CRM_CONNECTION_LINK_NAME`, then run health, negative preflight and CRM connection tests.
