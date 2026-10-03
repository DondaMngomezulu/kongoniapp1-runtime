# Zoho CRM SysML Capability Architecture

This package represents the governed architecture without redefining enterprise semantics.

## Authority
1. REG-STD-001 Enterprise Reference Standards Register — governed authority.
2. Governed Enterprise Dictionary — semantic concepts and lifecycle.
3. This Git repository — executable/model source.
4. Zoho Catalyst — integration/runtime.
5. Zoho CRM — operational implementation.

SysML is the system/capability representation. It is not the canonical dictionary.

## Controls
- SEM-010: MCP transports/exposes governed semantics and must not create parallel meaning.
- SEM-011: structural schema is separate from canonical field semantics and controlled values.
- SCOPE-001: concept definition/mapping owner.
- SCOPE-002: identifiers/controlled values owner.
- SCOPE-004: schema/business-rule validation owner.
- Draft and proposed dictionary concepts retain their lifecycle status.

## Test scope
The architecture tests check source authority, lifecycle preservation, capability-gap truthfulness, and separation of model/runtime concerns. They do not assert production business-rule conformance.
