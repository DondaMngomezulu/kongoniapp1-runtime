# Handoff — WRK-ZCRM-BP-001

## From
ChatGPT / Kongoni governance workflow

## To
Claude Agent operating from the `kongoniapp1-runtime` repository

## Current state

`BP-BIAN-AGR-001` exists in Zoho CRM as an inactive draft. Its structure has been read back successfully. The ChatGPT Zoho CRM plugin can create and read the Blueprint, but attempts to update Blueprint transitions return `OAUTH_SCOPE_MISMATCH`.

The next agent is authorised to test whether its own governed agent/MCP tools provide the required Zoho CRM transition-update capability.

## Required first action

Read:

1. `agent-workspace/AGENTS.md`
2. `mandate.yaml`
3. `instruction.md`
4. `plan.yaml`

Then execute only the canary defined in the mandate.

## Stop conditions

Stop without further mutation if:

- the Blueprint is no longer draft/inactive;
- the canary transition ID does not resolve to `Submit for Review`;
- the tool requires secret extraction or manual token handling;
- the requested operation would change business semantics;
- an OAuth or permission error persists.

## Handoff requirement

After the test, replace this file with the actual result and evidence references for the next agent.
