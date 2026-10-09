# Kongoni Enterprise Engineering Agent Rules

Applies to every human, ChatGPT, Claude, Codex, Zia and other automation actor modifying the enterprise engineering repository or implementing enterprise system configuration.

## Mandatory control: CTL-ENG-GH-ROUTE-001

Before any material development, application configuration, workflow/Blueprint edit, database migration, integration adjustment, policy/prompt update, infrastructure change or deployment:

1. Open or identify the accountable GitHub Issue. Record the route ID, mandate, target system, task class, risk and owner.
2. Resolve the active Catalyst architecture, Agent Contract and target EnvironmentExecutionAuthority. Do not infer execution permission from GitHub access.
3. Create an isolated branch and linked pull request; apply the repository PR template. Add a redacted configuration change record under `governance/configuration-changes/` for every relevant config change.
4. Include a same-change-set `agent-workspace/change-log/` record and objective evidence refs under CTL-DEV-CHG-LOG-001 and CTL-SYS-WRITE-AUDIT-001.
5. Require passing `enterprise-route-gate`, `validate-change-log` and `validate` checks, independent review and any reserved Group CEO approval before approval to release.
6. Execute only by approved GitHub Action or GitHub-initiated auditable gateway. Record issue, PR, commit SHA, run ID, platform receipt and before/after evidence. A GitHub PR alone is not authority to operate an external system.
7. Fail closed for T2/T3 configuration writes when protected branch, native connector/RBAC, environment approval or execution gateway are unverified. P0 break-glass needs separate explicit permission, tight scope, logging and retrospective PR within one business day.
8. Perform CHECK/STUDY and ACT before closure. `DO_COMPLETE != TASK_COMPLETE`.

Routine customer, finance or sales transactions already executed by approved business workflows remain in their native system of record; do not create a GitHub issue for each transaction. Never store credentials or customer/personally identifying or payment data in this public repository.

For workspace-specific additional rules see `agent-workspace/AGENTS.md`.
