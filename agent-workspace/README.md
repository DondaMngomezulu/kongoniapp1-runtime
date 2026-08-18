# Kongoni Governed Agent Workspace

This directory implements `PAT-AGT-COLLAB-001 — Governed Agent Shared Workspace Pattern`.

## Authority boundary

- **Zoho Catalyst** is the authoritative governance and execution-control plane.
- **GitHub** is the shared working and engineering workspace.
- **MCP** is the interoperable tool execution layer.
- **Agent Contracts** define execution authority.
- **KEA-MOD-HS-001** is the architecture constraint.
- **MET-PDCA-001** governs execution and closure.

Working files in this directory do not replace authoritative Catalyst records.

## Standard work-item structure

`work/<WORK-ID>/mandate.yaml` — machine-readable mandate and state.

`work/<WORK-ID>/instruction.md` — current execution instruction.

`work/<WORK-ID>/plan.yaml` — current plan and authorisation state.

`work/<WORK-ID>/handoff.md` — agent-to-agent handoff.

`work/<WORK-ID>/evidence/` — objective execution evidence.

`work/<WORK-ID>/tests/` — verification and validation cases.

`work/<WORK-ID>/outcome.yaml` — CHECK/STUDY and ACT outcome.

## State rule

`DO_COMPLETE != TASK_COMPLETE`.

A T2/T3 work item remains open until objective CHECK/STUDY evidence exists, an ACT decision is recorded, and the required authoritative Catalyst records are updated.