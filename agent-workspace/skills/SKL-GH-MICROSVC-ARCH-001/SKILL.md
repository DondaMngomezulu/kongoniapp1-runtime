---
name: github-microservice-architect
governed_id: SKL-GH-MICROSVC-ARCH-001
version: '1.0'
status: ADOPTED
owner: Chief of Accountability
technical_domain: Microservice architecture and governed specification
methodology: MET-PDCA-001
inherits:
  - CTL-DEV-CHG-LOG-001
  - CTL-SYS-WRITE-AUDIT-001
references:
  - governed enterprise architecture
  - approved reference standards such as BIAN, TM Forum, MIMOSA, APQC, FIBO, and others where applicable
  - Zoho Catalyst platform constraints when Catalyst is the target runtime
---

# GitHub Microservice Architect Skill

## 1. Purpose

Use this skill to define what a governed microservice must be.

The skill SHALL produce an approved or proposed Kongoni Service Specification in GitHub. It SHALL NOT implement or deploy the runtime service.

## 2. System role

GitHub is the authoritative engineering repository for the service architecture, specification, API contract, acceptance criteria, design decisions, version history, and architecture change evidence.

The Architect owns design intent. The Engineer owns implementation conformance.

## 3. Trigger

Use this skill when a task asks an agent to define, design, decompose, profile, crosswalk, or specify a microservice before implementation.

Use it when a reference standard such as BIAN must be converted into a Kongoni service design.

Do not use it to write Catalyst application code, deploy AppSail, deploy Functions, change API Gateway, or mutate Catalyst runtime resources.

## 4. Mandatory inputs

Resolve:

- service purpose;
- business owner;
- value stream;
- mandate;
- task class;
- reference standard and provenance where applicable;
- service boundary;
- primary resource;
- subordinate resources or functions;
- required operations;
- system-of-record decisions;
- integration requirements;
- security requirements;
- non-functional requirements;
- acceptance criteria;
- target platform constraints.

Missing normative inputs SHALL create a PLAN gap. The Architect SHALL NOT invent missing normative business semantics.

## 5. Reference-model mapping

When BIAN is the source, use this default mapping:

- Service Domain = candidate microservice boundary.
- Control Record = primary managed resource.
- Behaviour Qualifier = subordinate resource, capability, or functional component.
- Service Operation = candidate API operation or application command.

A BIAN Service Operation SHALL NOT automatically become a separate microservice.

The same principle applies to other standards: preserve the external reference model and create a separate Kongoni implementation profile.

## 6. Architecture decisions

The Architect SHALL define:

- service identifier and version;
- service purpose and responsibility;
- service boundary;
- ownership and value stream;
- primary resource and lifecycle;
- subordinate resources;
- operations and business semantics;
- API contract intent;
- event and integration requirements;
- system-of-record assignments;
- data ownership and retention requirements;
- security and authority requirements;
- audit requirements;
- runtime constraints, without choosing implementation detail unless required by architecture;
- availability, performance, resilience, and recovery requirements;
- acceptance criteria;
- dependencies;
- risks and architecture decisions.

## 7. Service boundary test

A proposed microservice SHALL have one coherent business responsibility.

Split a service only when there is objective evidence for a separate ownership, security, scaling, failure-isolation, data-sovereignty, lifecycle, or deployment boundary.

Merge overlapping service candidates when they manage the same business resource and lifecycle without a material independence requirement.

## 8. Data architecture

The Architect SHALL identify the canonical business object and system of record before any new implementation datastore is proposed.

The Architect SHALL check for duplicate or overlapping enterprise objects and SHALL define crosswalks where the same business concept has representations in CRM, Catalyst, Books, or another system.

The Service Specification SHALL distinguish canonical identity from application-specific representations.

## 9. API architecture

The Architect SHALL specify operation semantics, resource paths, request/response intent, error classes, authentication requirement, authorisation requirement, idempotency requirement for writes, correlation requirement, and audit requirement.

The Architect SHALL not prescribe a transport-specific implementation when the architecture does not require it.

## 10. Catalyst target profile

When Zoho Catalyst is the target runtime, the Architect SHALL identify platform constraints that affect the design, including candidate use of AppSail, Functions, API Gateway, Data Store, Connections, Circuits, Signals, Job Scheduling, Stratus, and observability.

The final runtime selection is an engineering decision unless the architecture has a material reason to constrain it.

## 11. Required output

The primary output is one governed Kongoni Service Specification stored in GitHub.

The specification SHALL include at minimum:

- service identity;
- semantic source and provenance;
- business ownership and value stream;
- service boundary;
- primary and subordinate resources;
- service operations;
- API contract requirements;
- data and system-of-record decisions;
- integration requirements;
- security and authority requirements;
- audit requirements;
- non-functional requirements;
- acceptance criteria;
- engineering constraints;
- unresolved gaps;
- PDCA status.

Supporting outputs can include architecture decision records, crosswalks, interface schemas, sequence or state models, and acceptance-test definitions.

## 12. Handover to Engineer

The Architect SHALL hand over only a specification that is sufficiently complete for implementation.

The handover state SHALL be one of:

- READY_FOR_ENGINEERING;
- ARCHITECTURE_GAP;
- AUTHORISATION_GAP;
- REJECTED.

The Engineer SHALL use the approved Service Specification as its authoritative build input.

If the Engineer finds an architecture defect, it SHALL return an ADAPT request to the Architect. The Engineer SHALL NOT silently redesign the service boundary or business semantics.

## 13. Governance workflow

Use:

MANDATE -> PLAN -> AUTHORISATION -> DO -> EVIDENCE -> CHECK/STUDY -> ACT -> RECORD -> CLOSE OR REPLAN.

For architecture work, DO means producing or updating the governed specification. DO_COMPLETE does not mean the architecture task is complete.

CHECK/STUDY SHALL test semantic completeness, boundary coherence, duplicate-object risk, reference-standard conformance, platform feasibility, security completeness, and acceptance-test completeness.

## 14. Failure conditions

Stop or return a gap when:

- the service boundary is ambiguous;
- the canonical business object is unresolved;
- the system of record is unresolved where it is material;
- normative source semantics are missing;
- a duplicate service or object is likely;
- security or authority requirements are missing;
- the target platform cannot support a required capability;
- acceptance criteria are not testable.

## 15. Current canary

The first canary is:

`SRV-BIAN-LEASING-001 — Leasing Service`

Source mapping:

- BIAN 14.0.0 Service Domain: Leasing.
- Control Record: LeasingFacility.
- 11 Behaviour Qualifiers.
- 44 Service Operations.

The first engineering handover can be limited to `Initiate`, `Retrieve`, and `Update` while retaining the full operation catalogue for later controlled increments.
