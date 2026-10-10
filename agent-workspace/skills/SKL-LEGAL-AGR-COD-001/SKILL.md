---
name: agreement-machine-codifier
governed_id: SKL-LEGAL-AGR-COD-001
version: '1.0'
status: DEVELOPMENT_IMPLEMENTED_ACT_PENDING
owner: Company Secretary & Legal Counsel
technical_domain: agreement semantic and normative codification
methodology: MET-PDCA-001
references:
  - OASIS LegalDocML / Akoma Ntoso 1.0
  - OASIS LegalRuleML 1.0
  - W3C JSON-LD 1.1
  - W3C RDF 1.1
  - W3C PROV-O
  - W3C SKOS
  - W3C SHACL
  - ISO 704 terminology principles
---

# Agreement Machine Codifier Skill

## 1. Purpose

Use this skill to convert an authoritative agreement and its governed supporting evidence into a reusable machine-readable legal record without changing the legal meaning of the source.

The skill produces a dual legal representation:

1. a structured legal-document record using OASIS LegalDocML / Akoma Ntoso; and
2. a normative legal-rule record using OASIS LegalRuleML.

It also produces a JSON-LD semantic projection and a governed package manifest for enterprise integration.

This skill is reusable across shareholder agreements, sale agreements, leases, finance agreements, service agreements, mandates, NDAs, amendments, deeds of adherence, side letters and other contractual instruments.

## 2. Governing rule

The signed or otherwise authoritative legal artifact remains the legal evidence source. Machine-readable records SHALL NOT replace the authoritative executed instrument unless applicable law and the parties expressly establish the machine-readable form as authoritative.

No fact, obligation, right, condition, remedy, date, party, definition or interpretation may be silently invented, corrected or completed.

Where the source is ambiguous, incomplete, inconsistent or illegible, record the uncertainty and route it to legal review.

## 3. Inputs

Mandatory input:

- authoritative agreement artifact or authoritative legal text;
- agreement identity or sufficient information to assign a governed agreement ID;
- provenance of the source artifact.

Conditional inputs:

- amendments, addenda, schedules and annexures;
- deeds of adherence or accession;
- notices and elections issued under the agreement;
- share certificates, registers or other title evidence;
- board/shareholder resolutions;
- correspondence relevant to interpretation or performance;
- governing legislation, MOI, policy or external normative source.

Supporting evidence SHALL remain distinguishable from the agreement text itself.

## 4. Output package

Each codification run SHALL produce an Agreement Machine-Readable Package containing, as applicable:

- `source/` authoritative source reference and cryptographic hash;
- `agreement.akn.xml` LegalDocML/Akoma Ntoso representation;
- `agreement.rules.lrml.xml` LegalRuleML representation;
- `agreement.jsonld` enterprise semantic projection;
- `manifest.yaml` governed package manifest;
- `validation.json` validation results and unresolved exceptions;
- `provenance.jsonld` provenance graph;
- optional `crosswalk.csv` clause-to-rule-to-concept mapping.

The package SHALL preserve stable identifiers so later amendments and notices can refer to the same clauses and rules.

## 5. Agreement identity

Assign or resolve:

- governed Agreement ID;
- agreement type;
- title;
- execution/signature date where evidenced;
- effective date where evidenced;
- governing law where evidenced;
- status: draft, executed, amended, terminated, expired, superseded or unknown;
- authoritative source artifact ID and hash;
- parties and contractual roles;
- related entities, assets, products and value streams where governed mappings exist.

Do not infer an effective date from a signature date unless the agreement makes that relationship clear.

## 6. LegalDocML / Akoma Ntoso codification

Represent the legal document hierarchy faithfully.

At minimum, where present, identify and encode:

- document metadata;
- parties and roles;
- recitals / background;
- definitions;
- clauses and subclauses;
- schedules and annexures;
- tables and lists;
- cross-references;
- dates, amounts and percentages;
- execution/signature blocks;
- amendment or version relationships.

Every materially operative clause and subclause SHALL have a stable machine-addressable identifier.

Preserve the source order. Do not reorganize clauses merely to improve machine processing.

## 7. LegalRuleML codification

Extract a LegalRuleML rule only where the source supports a normative proposition.

Classify rule expressions, as applicable, into:

- obligation;
- permission;
- prohibition;
- power / entitlement;
- condition precedent;
- trigger;
- deadline / temporal constraint;
- alternative election;
- deemed event;
- exception;
- remedy;
- default consequence;
- termination consequence;
- valuation mechanism;
- approval / consent requirement.

Each rule SHALL reference the source clause(s) from which it is derived.

A rule SHALL distinguish:

1. source-derived contractual norm;
2. factual assertion;
3. party interpretation or legal position; and
4. adjudicated or otherwise authoritative determination.

A party interpretation SHALL NOT be encoded as if it were an uncontested contractual norm.

## 8. Temporal rules

For every deadline or time-based rule, capture where evidenced:

- triggering event;
- duration;
- unit (business day, calendar day, month, year);
- start/exclusion rule;
- end/inclusion rule;
- time of day;
- business-day adjustment rule;
- timezone if stated or legally necessary;
- consequence of non-performance or silence.

Do not calculate an absolute deadline unless the trigger date is known and the agreement supplies sufficient counting rules.

## 9. Party and role model

Separate legal entity identity from contractual role.

Examples of contractual roles include seller, purchaser, lender, borrower, lessor, lessee, shareholder, company, guarantor, service provider, customer, offeror, offeree and agent.

A party may hold multiple roles. Roles SHALL be linked to the relevant clause or transaction context.

Use governed enterprise Entity/Agent identifiers where available. CRM or application object IDs SHALL NOT become semantic parents.

## 10. Definitions and terminology

Definitions SHALL be captured as governed terms with exact source provenance.

Where the same term has a different meaning in another agreement, preserve the agreement-specific definition and do not overwrite the enterprise concept.

Map agreement terms to enterprise SKOS concepts only when the semantic relationship is supportable. Use mappings such as exactMatch, closeMatch, broaderMatch or narrowerMatch deliberately.

## 11. Amounts, rates and formulas

Capture:

- monetary amount and currency;
- percentage or basis-point amount;
- pricing basis;
- interest benchmark and margin;
- compounding rule;
- day-count basis;
- valuation date;
- valuation method;
- calculation inputs;
- rounding rule where stated.

Do not infer an unstated formula. If an agreement refers to a defined method that is missing or undefined, record a validation exception.

## 12. Evidence and interpretation

Maintain an evidence graph linking material assertions to their sources.

Examples:

- registered ownership -> securities register / certificate;
- authority -> resolution / mandate;
- amendment -> signed amendment;
- strategic disagreement -> board minutes / correspondence;
- notice service -> sent-message evidence / receipt rule.

Evidence outside the agreement SHALL NOT silently amend the contractual text.

Where correspondence is without prejudice or subject to contract, record that status in provenance.

## 13. Amendment and lifecycle handling

Never overwrite an executed agreement record with amended text.

Maintain:

- original expression;
- each amendment/addendum expression;
- consolidated working expression where useful;
- effective-from and effective-to relationships where evidenced;
- clause-level amendment provenance.

A consolidated expression SHALL identify itself as derived and SHALL link back to all authoritative source instruments.

## 14. Validation gates

The codification SHALL fail closed for legal-operational use if any P0 exception exists.

P0 exceptions include:

- missing authoritative source;
- unresolved party identity affecting obligations;
- missing or duplicate clause identifiers;
- source text omitted from a material operative clause;
- machine rule contradicts source clause;
- unsupported invented obligation/right/remedy;
- unresolved amendment precedence affecting current rights;
- invalid XML against adopted schema where schema validation is required.

P1 exceptions include ambiguous dates, undefined terms, unresolved cross-references, incomplete signature evidence, unclear calculations and contested interpretations.

P1 items may be published only with explicit exception status and legal-review routing.

## 15. Human legal-review gate

Require Company Secretary & Legal Counsel review before a codified agreement is used to:

- issue a binding notice or election;
- calculate a contractual default or remedy;
- trigger payment, transfer, termination or enforcement;
- determine reserved-matter approval;
- infer waiver, breach or liability;
- generate an execution-ready legal instrument from the rule record.

The skill may prepare the record and identify the legal consequence, but shall not convert ambiguity into a binding conclusion without the required authority.

## 16. Enterprise semantic projection

The JSON-LD projection SHALL expose only governed semantic relationships.

Minimum entities:

- Agreement;
- AgreementType;
- Party / Agent;
- ContractualRole;
- Clause;
- LegalRule;
- Obligation / Permission / Prohibition / Power;
- Trigger / Condition;
- TemporalConstraint;
- MonetaryTerm;
- GoverningLaw;
- EvidenceArtifact;
- Amendment;
- Notice / Election where applicable.

Where enterprise mappings exist, bind Agreement to Value Stream, Product Type, Principal Agreement Type, Contractual Role Type(s), Counterparty Relationship and Entity/Agent.

## 17. Provenance

Every generated artifact SHALL record:

- source artifact identifier;
- source hash;
- extraction/codification timestamp;
- skill ID and version;
- actor/agent performing codification;
- governing standards;
- transformation version;
- validation status;
- unresolved exceptions;
- legal reviewer and approval state where applicable.

Use W3C PROV-O semantics in the JSON-LD provenance projection.

## 18. Idempotency and repeat runs

A repeat run against the same source hash and same skill/transformation version SHOULD produce semantically equivalent output.

A changed source hash SHALL create a new codification run and SHALL NOT silently replace the prior record.

## 19. Minimum workflow

Follow this sequence:

1. establish mandate and source authority;
2. inventory agreement and supporting artifacts;
3. hash and register authoritative source;
4. classify agreement and parties/roles;
5. structure clauses in LegalDocML;
6. extract source-derived norms into LegalRuleML;
7. build JSON-LD semantic projection;
8. bind provenance and evidence;
9. run schema, structural, semantic and rule validation;
10. produce exception register;
11. obtain legal review where required;
12. publish governed package;
13. record ACT decision and close or replan under MET-PDCA-001.

## 20. Prohibited behaviours

The skill SHALL NOT:

- invent missing contractual terms;
- treat a negotiation proposal as an executed amendment;
- treat a party's interpretation as an authoritative contractual rule;
- discard source text after semantic extraction;
- merge different legal entities because trade names appear similar;
- infer beneficial ownership from email correspondence when a securities register is available;
- replace a signed source artifact with a generated document;
- hide validation exceptions;
- promote a package to operative use without required legal review.

## 21. Acceptance rule

The Agreement Machine-Readable Package is `VALIDATED` only when:

- source provenance is complete;
- LegalDocML structure is traceable to source text;
- LegalRuleML rules are traceable to clauses;
- all material terms have stable identifiers;
- no P0 exception is open;
- JSON-LD projection does not contradict source semantics;
- required legal review has been completed for the intended use.

Otherwise the package status SHALL be `DRAFT`, `EXCEPTION`, or `LEGAL_REVIEW_REQUIRED`.