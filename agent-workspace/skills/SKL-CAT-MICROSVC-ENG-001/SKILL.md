---
name: zoho-catalyst-microservice-engineering
governed_id: SKL-CAT-MICROSVC-ENG-001
version: '0.2'
status: ADOPTED
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

Use this skill when a task asks an agent to create, change, test, deploy, or assess a Catalyst microservice, AppSail service, supporting Function, API Gateway route, service API, or BIAN-derived Catalyst service.

Do not use this skill for a read-only Catalyst administration question that does not change or design a service.

## 3. Mandatory inputs

Before implementation, resolve the service ID, name, purpose, owner, value stream, task class, mandate, target environment, runtime, language, primary resource, operations, data, security, audit, and test requirements.

When BIAN is the semantic source, also resolve the BIAN version, Service Domain, Control Record, Behaviour Qualifiers, Service Operations, and Semantic API source.

Missing material inputs SHALL cause a PLAN gap. The agent SHALL NOT invent normative business semantics.

## 4. Catalyst documentation gate

Before any Catalyst design, code, configuration, test, or deployment step, the agent SHALL load the relevant current Zoho Catalyst engineering reference for that step.

The documentation authority order is:

1. Official Zoho Catalyst documentation and current Catalyst platform conventions.
2. The installed Catalyst-by-Zoho engineering skill and its focused reference files that represent those conventions.
3. The Kongoni Service Specification and approved Kongoni implementation profiles.

The agent SHALL use the most focused reference that applies to the task. Typical references include:

- architecture patterns for service selection;
- AppSail and service documentation for AppSail work;
- Functions and SDK documentation for Functions;
- the Python, Java, or Node.js SDK reference for code that uses that SDK;
- cloud-scale documentation for Data Store, ZCQL, Cache, Stratus, and Authentication;
- API Gateway documentation before route or gateway changes;
- deployment SOPs and CLI reference before deployment;
- observability or DevOps documentation before production-readiness assessment;
- troubleshooting documentation when a Catalyst operation fails.

The agent SHALL NOT rely only on memory for a material Catalyst implementation detail when an applicable reference is available.

If the installed reference does not answer a specific API parameter, platform limit, or edge case, the agent SHALL verify the point against the current official Zoho Catalyst documentation before implementation.

The agent SHALL record the material documentation references used in the Service Specification or engineering evidence.

A material Catalyst implementation SHALL fail the PLAN gate when the required technical reference cannot be resolved with sufficient confidence.

## 5. Catalyst pre-flight gate

Before writing service code, the agent SHALL verify that the target Catalyst project is already initialized.

The working project SHALL contain `.catalystrc` and `catalyst.json`. The agent SHALL read both files before code changes.

The agent SHALL NOT manually create `.catalystrc`, `catalyst.json`, a Catalyst-managed `functions/` root created by interactive initialization, or a legacy `client/` implementation for a new frontend.

If the required project files are missing, the engineering task SHALL stop at the provisioning gate. Interactive `catalyst login`, `catalyst init`, and interactive function registration remain human-controlled steps unless an approved non-interactive method is available.

## 6. Service boundary rule

A microservice SHALL have one coherent business responsibility.

For a BIAN-derived service, the default mapping is:

- BIAN Service Domain = candidate microservice boundary.
- BIAN Control Record = primary managed resource.
- BIAN Behaviour Qualifier = subordinate resource or functional component.
- BIAN Service Operation = API operation or application command.

A Service Operation SHALL NOT automatically become a separate deployable microservice.

Split a Service Domain only when there is objective evidence for a separate scaling, security, ownership, failure-isolation, data-sovereignty, or deployment boundary.

## 7. Runtime and language selection

Use AppSail as the default runtime for a stable service boundary with multiple related API routes or richer middleware. Use a Function for a small event-oriented, scheduled, asynchronous, integration-focused, or narrow HTTP workload. Use Circuits for governed multi-step orchestration, Job Scheduling for scheduled execution, and Signals for event publication/subscription.

Select one primary server language for each deployable microservice unless there is a documented exception. The default Kongoni language is Python unless a material technical reason requires another supported language.

The runtime and language decisions SHALL be recorded with their reasons and verified against the current Catalyst documentation loaded under the documentation gate.

## 8. Service contract

Every microservice SHALL have an explicit service contract before implementation. The contract SHALL define the service identifier and version, API base path, operations, HTTP methods, request and response schemas, error schema, authentication, authorisation, idempotency for writes, timeout, retry, correlation ID, and audit requirement.

When a BIAN Semantic API exists, preserve BIAN operation semantics unless a governed Kongoni profile explicitly changes them.

## 9. Data design

Before creating a new Catalyst Data Store table, the agent SHALL search for an existing canonical object, check duplicate or overlapping tables, identify the system of record, define keys and relationships, define lifecycle and retention requirements, define access controls, and assess migration impact.

Do not create one table for every process step or Behaviour Qualifier unless the data model requires it.

## 10. API Gateway

External or cross-application HTTP access SHOULD use Catalyst API Gateway when it is the approved ingress layer.

Before enabling or changing API Gateway, define and test routes, authentication, authorisation, throttling where required, request validation, error responses, CORS where applicable, and regression impact on existing routes.

API Gateway activation is a controlled change because it can affect existing access paths.

## 11. Security and write audit

The service SHALL apply least privilege. Secrets SHALL NOT be stored in source code, logs, audit records, test fixtures, or GitHub change records. Use approved Catalyst Connections or other governed secret mechanisms for external credentials.

Every write operation SHALL resolve execution authority before mutation. T2 and T3 writes SHALL fail closed when authority or audit evidence is insufficient.

Every material system write SHALL comply with `CTL-SYS-WRITE-AUDIT-001` when that control is active. Repository changes SHALL also comply with `CTL-DEV-CHG-LOG-001`.

## 12. Observability

Every production candidate SHALL define structured application logs, correlation IDs, error logging without secrets, a health check, operational metrics where supported, alert conditions for material failures, and an evidence source for CHECK/STUDY.

A service without sufficient operational evidence SHALL NOT be promoted as production-ready.

## 13. Engineering workflow

Use the canonical sequence:

MANDATE -> PLAN -> AUTHORISATION -> DO -> EVIDENCE -> CHECK/STUDY -> ACT -> RECORD -> CLOSE OR REPLAN.

At PLAN, resolve the Service Specification and load the required Catalyst documentation. At AUTHORISATION, verify execution authority. At DO, implement only the authorised scope. At EVIDENCE, record code, configuration, tests, runtime IDs, deployment IDs, logs, audit events, and documentation references. At CHECK/STUDY, compare expected with actual behaviour and perform regression assessment. At ACT, record ADOPT, ADAPT, REPEAT, REJECT, or ESCALATE.

Do not close material work at DO_COMPLETE.

## 14. Minimum test set

A production candidate SHALL pass, where applicable, schema validation, unit tests, service-contract tests, authentication tests, authorisation tests, idempotency tests, negative-input tests, error-contract tests, data-integrity tests, integration tests, audit-event tests, health-check tests, regression tests, deployment smoke tests, and rollback or recovery tests for material changes.

## 15. BIAN implementation workflow

When the source is BIAN:

1. Read the governed BIAN Service Domain record.
2. Confirm the BIAN version and provenance.
3. Read the Control Record.
4. Read the Behaviour Qualifiers.
5. Read the Service Operations.
6. Read the Semantic API contract where available.
7. Load the applicable Catalyst technical references.
8. Select only the operations needed for the authorised Kongoni scope.
9. Create or update the Kongoni Service Specification.
10. Add Kongoni technical requirements that BIAN does not define.
11. Implement in Catalyst.
12. Test BIAN semantic conformance and Catalyst technical conformance separately.

Do not modify the normative BIAN source records to hold Catalyst-specific implementation details.

## 16. Required outputs

A completed engineering cycle SHALL produce or update the governed Service Specification, source code, API contract, data schema or mapping, runtime configuration, security and authority mapping, automated tests, deployment references, documentation references, change-log record, system-write audit records for material writes, CHECK/STUDY evidence, ACT decision, and handoff or closure record.

## 17. Failure conditions

Stop or fail closed when the Catalyst project is not correctly initialized, the required Catalyst technical reference cannot be resolved, the service boundary is ambiguous, normative business semantics are missing, the target environment is not authorised, credentials would need to be committed, a T2/T3 write cannot be audited, a new data object duplicates an existing canonical object, the API contract and implementation do not match, required tests fail, or production promotion lacks explicit authority.

## 18. Canary implementation

The first canary is `SRV-BIAN-LEASING-001 — Leasing Service`.

Default mapping:

- Service Domain: Leasing.
- Primary resource: `LeasingFacility`.
- Candidate runtime: AppSail.
- Default language: Python, subject to current runtime and SDK documentation validation.
- Ingress: Catalyst API Gateway when approved.
- Persistence: governed Catalyst data model.
- Audit: enterprise system-write audit control.

Start with `Initiate`, `Retrieve`, and `Update`. Add Behaviour Qualifier operations only after the core resource contract passes its tests.
