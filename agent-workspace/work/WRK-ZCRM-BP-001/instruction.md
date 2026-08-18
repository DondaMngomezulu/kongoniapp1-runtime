# Claude Agent Instruction — WRK-ZCRM-BP-001

Read `agent-workspace/AGENTS.md` and `mandate.yaml` before doing any work.

## Objective

Use the tools available to your Claude environment to determine whether you can complete the Zoho CRM Blueprint transition update that is currently blocked through the ChatGPT Zoho CRM plugin.

The target is an existing **draft** Blueprint:

- Blueprint: `BP-BIAN-AGR-001`
- Blueprint ID: `5643538000008286023`
- Module: Agreements / `CustomModule14`
- Target canary transition: `Submit for Review`
- Transition ID: `5643538000008286001`

The ChatGPT Zoho CRM plugin can create and read the Blueprint, but an update to this transition returns `OAUTH_SCOPE_MISMATCH`. The suspected missing Zoho OAuth permission is `ZohoCRM.settings.transitions.UPDATE`.

## Required execution

1. Discover the tools available in your Claude environment. Specifically look for:
   - Zoho CRM MCP tools;
   - Zoho/CRM agent tools;
   - connected MCP servers;
   - other authorised agent tools that expose Zoho CRM Blueprint settings.
2. Prefer an existing governed agent/MCP tool over raw HTTP, personal access tokens, copied OAuth tokens, or manual credential handling.
3. Inspect the effective capabilities of the selected tool. Do not display secrets.
4. Verify that `BP-BIAN-AGR-001` exists and is still a draft before mutation.
5. Verify that transition `5643538000008286001` is the `Submit for Review` transition.
6. Attempt **one** controlled canary update to that transition using the agent/MCP tool.
   - The purpose is to cause the transition to receive a valid post-create modification/update so Zoho records `modified_time` and the Blueprint UI can render it correctly.
   - Do not change its business meaning, source state, target state, or activation status.
   - If the tool requires a full transition payload, read the current transition first and preserve its current values.
7. Read the transition and Blueprint back after the update.
8. Confirm whether the update succeeded and whether the Blueprint remains draft/inactive.
9. Record evidence in this work item. Update `handoff.md` and `outcome.yaml`.

## Hard controls

Do **not**:

- activate or publish the Blueprint;
- update the other 10 transitions during this test;
- create, update, or delete CRM business records;
- delete or recreate the Blueprint;
- change Agreement lifecycle semantics;
- change the Agreement schema;
- create a new OAuth client merely to bypass the plugin;
- expose credentials, OAuth access tokens, refresh tokens, cookies, passwords, or secrets;
- commit secrets to GitHub.

If the available agent tools also fail with an OAuth/scope/permission error, stop. Record the exact tool used, the non-secret error code/message, and the scope/capability that appears to be missing.

If the canary succeeds, stop after read-back verification. Do not normalise the remaining transitions without further authority.

## Evidence required

Record:

- Claude environment/tool used;
- MCP server or agent-tool name;
- target Blueprint ID;
- target transition ID;
- before-state summary;
- mutation result;
- after-state summary;
- Blueprint active/draft status after the test;
- any OAuth or permission error;
- whether CRM business records were changed (must be `false`);
- recommended ACT decision: `ADOPT`, `ADAPT`, `REPEAT`, `REJECT`, or `ESCALATE`.

## Success criterion

The canary succeeds only if the transition update completes through an authorised agent/MCP tool, the transition can be read back afterwards, the Blueprint remains draft/inactive, and no CRM business record is changed.
