---
name: zoho-catalyst-microservice-engineer
governed_id: SKL-CAT-MICROSVC-ENG-001
version: '1.0'
status: ADOPTED
owner: Chief of Accountability
technical_domain: Zoho Catalyst microservice implementation
methodology: MET-PDCA-001
inherits:
  - CTL-DEV-CHG-LOG-001
  - CTL-SYS-WRITE-AUDIT-001
references:
  - approved Kongoni Service Specification
  - current Zoho Catalyst official documentation and installed Catalyst engineering references
---

# Zoho Catalyst Microservice Engineer Skill

## 1. Purpose

Use this skill to implement an approved Kongoni Service Specification on Zoho Catalyst.

The Engineer answers: how do we build the approved service correctly on Catalyst?

The Engineer SHALL NOT redefine the service boundary, business semantics, canonical object, or value-stream ownership. Architecture changes SHALL be returned to `SKL-GH-MICROSVC-ARCH-001` as an ADAPT request.

## 2. Authoritative input

The mandatory build input is an approved or authorised Kongoni Service Specification produced under `SKL-GH-MICROSVC-ARCH-001` or an equivalent governed architecture process.

The specification SHALL provide enough information to resolve:

- service ID and version;
- target environment;
- primary resource;
- required operations;
- API contract requirements;
- data/system-of-record decisions;
- security and authority requirements;
- audit requirements;
- non-functional requirements;
- acceptance criteria.

If a material architecture input is missing or contradictory, stop implementation and return an architecture gap.

## 3. Catalyst documentation gate

Before Catalyst design-detail, code, configuration, test, or deployment work, load the relevant current Zoho Catalyst technical reference.

Use the current official Catalyst documentation and the installed Catalyst-by-Zoho reference set for the specific service being changed. Typical references include AppSail, Functions and SDKs, Python/Java/Node SDKs, Data Store and ZCQL, Authentication, API Gateway, deployment SOPs, CLI, observability, DevOps, and troubleshooting.

Do not rely only on memory for a material Catalyst platform detail when a current reference is available.

Record material documentation references in engineering evidence.

## 4. Project pre-flight gate

Before writing application code, verify that `.catalystrc` and `catalyst.json` exist and read them.

Do not manually create `.catalystrc`, `catalyst.json`, a Catalyst-managed `functions/` root, or a legacy `client/` implementation for a new frontend.

If the project is not initialized, stop at the provisioning gate. Interactive `catalyst login`, `catalyst init`, and interactive function registration remain human-controlled unless an approved non-interactive method exists.

## 5. Runtime implementation

Select the Catalyst runtime that best implements the approved specification.

Use AppSail for a stable service with multiple related routes or richer middleware. Use a Function for a narrow HTTP, event, scheduled, asynchronous, or integration workload. Use Circuits for governed multi-step orchestration, Job Scheduling for scheduled execution, and Signals for event-driven integration.

The Engineer SHALL record the runtime decision and technical reason. If the selected runtime would change a material architecture property, return the decision to the Architect before implementation.

## 6. Language and SDK

Use one primary server language per deployable microservice unless an approved exception exists.

Python is the Kongoni default unless current Catalyst support, SDK coverage, performance, library maturity, security, maintainability, or interoperability gives a material reason to use another supported runtime.

Load the applicable SDK documentation before using a Catalyst SDK.

## 7. Implementation conformance

Implement the approved service contract without changing its business meaning.

The implementation SHALL conform to the approved operation semantics, route intent, request/response schemas, error contract, authentication, authorisation, idempotency, timeout, retry, correlation, and audit requirements.

For BIAN-derived services, preserve the approved BIAN/Kongoni semantic mapping in the Service Specification.

## 8. Data implementation

Before creating a new Catalyst Data Store object, verify the Service Specification system-of-record decision and search for existing canonical or overlapping objects.

Do not create a new table merely because an operation or Behaviour Qualifier exists.

Implement keys, relationships, validation, retention, migration, and access controls required by the specification.

If implementation reveals a duplicate or conflicting canonical object, stop and return an architecture gap.

## 9. Integration and API Gateway

Implement API Gateway only when required by the approved specification or approved platform pattern.

Before enabling or changing API Gateway, test routes, authentication, authorisation, request validation, throttling where required, errors, CORS where applicable, and regression impact.

Use approved Catalyst Connections or governed secret mechanisms for external credentials.

## 10. Security and authority

Apply least privilege.

Do not place secrets in source, logs, test fixtures, audit records, or GitHub change records.

Resolve execution authority before every material write. T2 and T3 writes SHALL fail closed when authority or audit evidence is insufficient.

Production requires separate explicit authority.

## 11. Write audit

Every material system write SHALL comply with `CTL-SYS-WRITE-AUDIT-001` when active.

Preserve the correlation ID, actor, mandate/task reference, target, requested change, before-state reference where applicable, result, after-state reference, native transaction/event reference where available, timestamp, and evidence reference.

Repository changes SHALL comply with `CTL-DEV-CHG-LOG-001`.

## 12. Observability

Every production candidate SHALL have structured logs, correlation IDs, secret-safe error logging, health checks, operational metrics where supported, material-failure alerts, and evidence that can support CHECK/STUDY.

## 13. Engineering workflow

Use:

MANDATE -> PLAN -> AUTHORISATION -> DO -> EVIDENCE -> CHECK/STUDY -> ACT -> RECORD -> CLOSE OR REPLAN.

At PLAN, read the approved Service Specification, Catalyst project files, and required Catalyst documentation. At AUTHORISATION, verify environment execution authority. At DO, implement only the authorised scope. At EVIDENCE, record code and configuration changes, tests, runtime IDs, deployment IDs, logs, audit events, and documentation references. At CHECK/STUDY, compare the implementation with the approved Service Specification and perform regression assessment. At ACT, record ADOPT, ADAPT, REPEAT, REJECT, or ESCALATE.

DO_COMPLETE does not mean TASK_COMPLETE.

## 14. Minimum test set

Where applicable, run:

- schema validation;
- unit tests;
- service-contract tests;
- authentication tests;
- authorisation tests;
- idempotency tests for writes;
- negative-input tests;
- error-contract tests;
- data-integrity tests;
- integration tests;
- audit-event tests;
- health-check tests;
- regression tests;
- deployment smoke tests;
- rollback or recovery tests for material changes.

The Engineer SHALL also run an implementation-conformance test against the approved Service Specification.

## 15. Required outputs

The primary output is a tested Zoho Catalyst microservice implementation.

The engineering cycle SHALL produce or update:

- source code;
- Catalyst runtime configuration;
- implemented API contract;
- data schema or mapping;
- integration configuration;
- security and authority mapping;
- automated tests;
- deployment references;
- runtime IDs;
- logs and operational evidence;
- system-write audit records;
- repository change records;
- implementation-conformance result;
- CHECK/STUDY evidence;
- ACT decision;
- handoff or closure record.

The approved Service Specification remains the architecture authority. The Engineer may update implementation evidence in it only as allowed by its governance rules.

## 16. Failure and return-to-architect conditions

Stop implementation and return `ADAPT -> SKL-GH-MICROSVC-ARCH-001` when:

- the service boundary is not implementable as specified;
- the canonical resource or system of record is unclear;
- required operations conflict;
- a target platform limit changes the architecture materially;
- the required security model cannot be implemented;
- a duplicate canonical object is found;
- acceptance criteria are not testable;
- implementation would require a change to normative business semantics.

Fail closed when the project is not initialized, target environment is not authorised, secrets would need to be committed, a T2/T3 write cannot be audited, required tests fail, or production promotion lacks authority.

## 17. Current canary

The first canary is `SRV-BIAN-LEASING-001 — Leasing Service`.

The Engineer receives the approved Service Specification from the GitHub Architect. The first implementation scope is `Initiate`, `Retrieve`, and `Update` for `LeasingFacility`. The remaining BIAN operations are later controlled increments unless the Architect changes the authorised scope.
