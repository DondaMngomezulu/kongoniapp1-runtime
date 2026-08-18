---
name: zoho-catalyst-microservice-engineering
governed_id: SKL-CAT-MICROSVC-ENG-001
version: '0.1'
status: PROPOSED
owner: Chief of Accountability
technical_domain: Zoho Catalyst microservice engineering
methodology: MET-PDCA-001
inherits:
  - CTL-DEV-CHG-LOG-001
  - CTL-SYS-WRITE-AUDIT-001
references:
  - Zoho Catalyst official development conventions
  - BIAN Service Landscape and Semantic APIs when BIAN is the service source
---

# Zoho Catalyst Microservice Engineering Skill

## 1. Purpose

Use this skill to design, build, test, deploy, change, or assess a microservice on Zoho Catalyst.

The skill converts a governed business service specification into a Catalyst implementation.

The skill SHALL keep these layers separate:

1. Business semantics.
2. Service contract.
3. Runtime implementation.
4. Security and authority.
5. Data persistence.
6. Observability and audit.
7. Deployment and validation.

## 2. Trigger

Use this skill when a task asks an agent to:

- create a Catalyst microservice;
- convert a BIAN Service Domain into a Catalyst service;
- create an AppSail service;
- create or modify a Catalyst Function that forms part of a microservice;
- expose a service through Catalyst API Gateway;
- define a Catalyst service API;
- implement a service operation;
- change an existing Catalyst microservice;
- test or deploy a Catalyst microservice.

Do not use this skill for a read-only Catalyst administration question that does not change or design a service.

## 3. Mandatory inputs

Before implementation, resolve these inputs:

- `service_id`
- `service_name`
- `service_purpose`
- `business_owner`
- `value_stream_id`
- `task_class`
- `mandate_ref`
- `target_environment`
- `runtime_type`
- `runtime_language`
- `primary_resource`
- `service_operations`
- `data_requirements`
- `security_requirements`
- `audit_requirements`
- `test_requirements`

When BIAN is the semantic source, also resolve:

- `bian_version`
- `bian_service_domain`
- `bian_control_record`
- `bian_behaviour_qualifiers`
- `bian_service_operations`
- `bian_semantic_api_source`

Missing material inputs SHALL cause a PLAN gap. The agent SHALL NOT invent normative business semantics.

## 4. Catalyst pre-flight gate

Before writing service code, the agent SHALL verify that the target Catalyst project is already initialized.

The working project SHALL contain:

- `.catalystrc`
- `catalyst.json`

The agent SHALL read both files before code changes.

The agent SHALL NOT manually create:

- `.catalystrc`
- `catalyst.json`
- a Catalyst-managed `functions/` root created by interactive initialization
- a legacy `client/` implementation for a new frontend

If the required project files are missing, the engineering task SHALL stop at the provisioning gate. Interactive `catalyst login`, `catalyst init`, and interactive function registration remain human-controlled steps unless an approved non-interactive method is available.

## 5. Service boundary rule

A microservice SHALL have one coherent business responsibility.

For a BIAN-derived service, the default mapping is:

- BIAN Service Domain = candidate microservice boundary.
- BIAN Control Record = primary managed resource.
- BIAN Behaviour Qualifier = subordinate resource or functional component.
- BIAN Service Operation = API operation or application command.

A Service Operation SHALL NOT automatically become a separate deployable microservice.

Split a Service Domain into more than one microservice only when there is objective evidence for a separate scaling, security, ownership, failure-isolation, data-sovereignty, or deployment boundary.

## 6. Runtime selection

Use `AppSail` as the default runtime when the service:

- has multiple related API routes;
- requires a web framework;
- has a stable long-lived service boundary;
- needs independent service packaging;
- requires richer middleware or routing.

Use a `Function` when the workload is small and event-oriented, scheduled, asynchronous, integration-focused, or a narrow HTTP operation.

Use `Circuits` for governed orchestration when a multi-step workflow needs explicit state, retries, branching, or compensation.

Use `Job Scheduling` for scheduled execution.

Use `Signals` when event publication and subscription are the correct integration pattern.

The runtime choice SHALL be recorded in the service specification with its reason.

## 7. Language selection

Select one primary server language for each deployable microservice unless there is a documented exception.

Supported Catalyst server runtimes include Node.js, Java, and Python where the selected Catalyst service supports them.

The default Kongoni language is Python unless a material technical reason requires another supported language.

The language decision SHALL consider:

- Catalyst runtime support;
- required SDK support;
- library maturity;
- performance;
- maintainability;
- security;
- team support;
- interoperability.

Do not select a language only because an agent prefers it.

## 8. Service contract

Every microservice SHALL have an explicit service contract before implementation.

The contract SHALL define:

- service identifier and version;
- API base path;
- operations;
- HTTP method where applicable;
- request schema;
- response schema;
- error schema;
- authentication requirement;
- authorisation requirement;
- idempotency rule for write operations;
- timeout rule;
- retry rule where applicable;
- correlation identifier;
- audit requirement.

When a BIAN Semantic API exists, preserve BIAN operation semantics unless a governed Kongoni profile explicitly changes them.

## 9. Data design

The microservice SHALL own or clearly reference the data needed for its responsibility.

Before creating a new Catalyst Data Store table, the agent SHALL:

1. search for an existing canonical object;
2. check for duplicate or overlapping tables;
3. identify the system of record;
4. define keys and relationships;
5. define lifecycle and retention requirements;
6. define access controls;
7. define migration impact.

Do not create one table for every process step or Behaviour Qualifier unless the data model requires it.

## 10. API Gateway

External or cross-application HTTP access SHOULD use Catalyst API Gateway when it is the approved ingress layer.

Before enabling or changing API Gateway, define and test:

- routes;
- authentication;
- authorisation;
- rate or throttle controls where required;
- request validation;
- error responses;
- CORS where applicable;
- regression impact on existing routes.

API Gateway activation is a controlled change because it can affect existing access paths.

## 11. Security

The service SHALL apply least privilege.

The service SHALL NOT contain secrets in source code, logs, audit records, test fixtures, or GitHub change records.

Use approved Catalyst Connections or other governed secret mechanisms for external credentials.

Every write operation SHALL resolve execution authority before mutation.

T2 and T3 writes SHALL fail closed when authority or audit evidence is insufficient.

## 12. Write audit

Every material system write SHALL comply with `CTL-SYS-WRITE-AUDIT-001` when that control is active.

The service SHALL preserve, where available:

- correlation ID;
- actor or calling principal;
- mandate or task reference;
- target resource;
- requested change;
- before-state reference;
- result;
- after-state reference;
- native Catalyst transaction or event reference;
- timestamp;
- evidence reference.

Repository changes SHALL also comply with `CTL-DEV-CHG-LOG-001`.

## 13. Observability

Every production candidate SHALL define:

- structured application logs;
- correlation IDs;
- error logging without secrets;
- health check;
- operational metrics where supported;
- alert conditions for material failures;
- evidence source for CHECK/STUDY.

A service without sufficient operational evidence SHALL NOT be promoted as production-ready.

## 14. Engineering workflow

Use this sequence:

### MANDATE
Confirm the authorised outcome, scope, service owner, value stream, task class, and environment.

### PLAN
Resolve the service specification. Map business semantics, operations, data, security, runtime, dependencies, tests, deployment, and rollback.

### AUTHORISATION
Verify execution authority for the target environment. Production requires separate authority.

### DO
Implement only the authorised scope. Keep business logic separate from transport, persistence, and platform adapters where practical.

### EVIDENCE
Record code changes, configuration changes, test results, runtime IDs, deployment IDs, logs, and audit events.

### CHECK/STUDY
Run the required tests and compare expected with actual behaviour. Include regression assessment.

### ACT
Record one decision: `ADOPT`, `ADAPT`, `REPEAT`, `REJECT`, or `ESCALATE`.

### RECORD
Update the authoritative service specification, change log, runtime registry, and evidence references.

### CLOSE OR REPLAN
Do not close material work at `DO_COMPLETE`.

## 15. Minimum test set

A production candidate SHALL pass, where applicable:

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
- health-check test;
- regression tests;
- deployment smoke test;
- rollback or recovery test for material changes.

## 16. BIAN implementation workflow

When the source is BIAN:

1. Read the governed BIAN Service Domain record.
2. Confirm the BIAN version and provenance.
3. Read the Control Record.
4. Read the Behaviour Qualifiers.
5. Read the Service Operations.
6. Read the Semantic API contract where available.
7. Select only the operations needed for the authorised Kongoni scope.
8. Create or update the Kongoni Service Specification.
9. Add Kongoni technical requirements that BIAN does not define.
10. Implement in Catalyst.
11. Test semantic conformance and technical conformance separately.

Do not modify the normative BIAN source records to hold Catalyst-specific implementation details.

## 17. Required outputs

A completed engineering cycle SHALL produce or update:

- governed Service Specification;
- source code;
- API contract;
- data schema or mapping;
- runtime configuration;
- security and authority mapping;
- automated tests;
- deployment manifest references;
- change-log record;
- system-write audit records for material writes;
- CHECK/STUDY evidence;
- ACT decision;
- handoff or closure record.

## 18. Failure conditions

Stop or fail closed when:

- the Catalyst project is not correctly initialized;
- the service boundary is ambiguous;
- normative business semantics are missing;
- the target environment is not authorised;
- credentials would need to be committed to source control;
- a T2/T3 write cannot be audited;
- a new datastore object duplicates an existing canonical object;
- the API contract and implementation do not match;
- required tests fail;
- production promotion lacks explicit authority.

## 19. Canary implementation

The first recommended canary is the BIAN `Leasing` Service Domain.

Candidate service:

`SRV-BIAN-LEASING-001 — Leasing Service`

Default mapping:

- Service Domain: Leasing.
- Primary resource: `LeasingFacility`.
- Candidate runtime: AppSail.
- Default language: Python, subject to runtime and SDK validation.
- Ingress: Catalyst API Gateway when approved.
- Persistence: governed Catalyst data model.
- Audit: enterprise system-write audit control.

Start with a small operation subset. Recommended first operations are `Initiate`, `Retrieve`, and `Update`. Add Behaviour Qualifier operations only after the core resource contract passes its tests.
