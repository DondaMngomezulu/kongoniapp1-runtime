# Kongoni Governed Agent Workspace

This directory implements `PAT-AGT-COLLAB-001 — Governed Agent Shared Workspace Pattern`.

## Authority boundary

`agent-workspace` is an engineering execution, collaboration and evidence workspace. It is **not** an enterprise system of record and it is **not** a legal, accounting, tax, commercial or business authority.

Authority is resolved by governed object class:

- **GitHub** is the governed engineering repository for code, schemas, validators, engineering work items, engineering evidence and change-control records.
- **Zoho Catalyst** is the execution/runtime and governance-control platform where the applicable governed architecture, execution authority or runtime records are designated authoritative.
- **Governed enterprise Catalogues, Libraries, Registers and Matrices** remain authoritative only according to their own adopted authority designation; copies or projections under `agent-workspace` do not supersede them.
- **External authoritative sources** such as legislation, regulations, IFRS, SARS material, standards and executed agreements retain their own normative authority; a machine-readable representation does not replace its source authority.
- **MCP** is an interoperable tool execution layer and has no independent business authority.
- **Agent Contracts** define agent execution authority but do not create business authority beyond the approved mandate.

A validator confirms conformance of an engineering artifact. A validator does **not** make that artifact the source of truth.

Working files, representations, cached copies, crosswalks and validation records in this directory SHALL NOT be interpreted as competing systems of record.

See `governance/agent-workspace-authority-boundary-v0.1.yaml`.

## Standard work-item structure

`work/<WORK-ID>/mandate.yaml` — machine-readable engineering mandate and state.

`work/<WORK-ID>/instruction.md` — current execution instruction.

`work/<WORK-ID>/plan.yaml` — current plan and authorisation state.

`work/<WORK-ID>/handoff.md` — agent-to-agent handoff.

`work/<WORK-ID>/evidence/` — objective engineering evidence and references to authoritative evidence.

`work/<WORK-ID>/tests/` — verification and validation cases.

`work/<WORK-ID>/outcome.yaml` — CHECK/STUDY and ACT outcome.

## State rule

`DO_COMPLETE != TASK_COMPLETE`.

A T2/T3 work item remains open until objective CHECK/STUDY evidence exists, the required ACT decision is recorded, and any required authoritative enterprise/runtime records are updated in their designated authoritative locus.