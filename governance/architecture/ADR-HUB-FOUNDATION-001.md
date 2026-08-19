# ADR-HUB-FOUNDATION-001 — Enterprise Hub Foundation Programme

## Status
ADOPTED

## Decision date
2026-08-19

## Parent architecture
`STD-ARCH-HUB-SPOKE-001 — Enterprise Brain-and-Nervous-System Hub Architecture`

## Decision
Kongoni Group adopts the four-foundation Hub Foundation Programme as the parent architecture and engineering programme for the enterprise microservice workstream.

The Enterprise Hub is a logical architectural role. It is the enterprise **Brain + Nervous System**. No single technology platform, including Zoho Catalyst, Google Cloud, OpenAI, MCP infrastructure, or any future platform, is synonymous with the Hub.

RAMI 4.0 layers are used as a classification and completeness guide. They are not mandatory deployment tiers.

## Foundation 1 — Identity & Authority
Capabilities:
- Canonical Enterprise Identity & Binding
- Enterprise Policy Decision
- Repository Routing Authority
- Canonical Spoke / Resource Registration

Engineering priority starts with `SRV-HUB-IDENTITY-001 — Canonical Enterprise Identity & Binding Service`.

## Foundation 2 — Nervous-System Contract
Capabilities:
- Canonical Message / Event Envelope
- Integration Reliability Control
- Enterprise Event Backbone

The event architecture SHALL remain vendor-neutral at the logical layer. Catalyst Signals, Google Pub/Sub / Eventarc, or another approved service may implement the capability through a governed runtime binding.

## Foundation 3 — Connectivity
Capabilities:
- Enterprise Integration Connector Catalogue
- Cross-Platform Orchestration Abstraction

Business/domain microservices SHALL consume governed connector and orchestration contracts rather than embed vendor-specific integration logic independently.

## Foundation 4 — Observability
Capabilities:
- Cross-platform logs, metrics and traces
- Correlation and causation identifiers
- Enterprise object, service, agent, value-stream and decision context
- Execution evidence for controlled CHECK/STUDY

## RAMI orientation
- Business: mandates, policy, authority, risk and value-stream coordination — Brain
- Functional: reasoning, decisioning, planning, agents, optimisation and orchestration — Brain
- Information: semantics, canonical identity, provenance, context and state bindings — Brain
- Communication: APIs, MCP, events, signals, queues and messages — Nervous System
- Integration: connectors, adapters, transformations and synchronisation — Nervous System
- Asset: applications, systems, machines and authoritative spokes — Sense / Actuate boundary

## Platform placement rule
Logical Hub capabilities SHALL be defined independently of their implementation platform.

Runtime selection between Zoho Catalyst, Google Cloud, OpenAI-hosted or MCP-enabled services, and other approved platforms SHALL be made through a governed placement decision based on proximity to authoritative state, scale, AI capability, eventing, portability, observability, security and cross-platform coordination.

Current default interpretation:
- Zoho Catalyst: Zoho-native business execution runtime and selected Hub services.
- Google Cloud: composable enterprise-scale compute, eventing, integration, data, observability and AI infrastructure.
- OpenAI: approved cognitive / agent capability implementation.
- MCP: governed digital nerve protocol between agents and enterprise capabilities.
- MTN Enterprise: candidate physical connectivity, edge and field nervous-system implementation.

## Microservice Register inheritance
The Enterprise Microservice Register SHALL inherit this programme. Microservice architecture records SHALL distinguish:
- logical capability;
- service contract;
- authoritative information source;
- runtime binding;
- connector / event contract;
- identity and policy dependencies;
- observability requirements;
- engineering handover evidence.

APQC sector-specific L3/L4/L5 and applicable domain standards (including BIAN, MIMOSA and other adopted references) remain valid decomposition and semantic inputs. One architectural concept SHALL NOT automatically become one microservice.

## Successor PDCA work
The following are successor controlled cycles and remain open until separately completed:
1. `SRV-HUB-IDENTITY-001` engineering.
2. Policy Decision and Repository Routing implementation.
3. Hub Runtime Placement Matrix — Catalyst vs Google Cloud and other approved runtimes.
4. Google Cloud-hosted Kongoni MCP service pattern.
5. Vendor-neutral event backbone contract and runtime selection.
6. Identity implementation assessment, including Zoho Directory and Google identity services.
7. Population of the Enterprise Microservice Register across value-stream service domains.
8. Standard Catalyst Development Runtime Profile provisioning.
9. Separate LCC Data Store payload to Stratus migration cycle.

## Governance
`MET-PDCA-001` and `BR-PDCA-001` apply to all successor material work.

Canonical rule: `DO_COMPLETE != TASK_COMPLETE`.

T2/T3 implementation remains open until objective CHECK/STUDY evidence, an explicit ACT decision, and required authoritative record updates exist.
