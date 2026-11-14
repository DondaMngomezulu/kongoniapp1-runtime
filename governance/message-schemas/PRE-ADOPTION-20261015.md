# Pre-adoption test assessment — 15 October 2026
Status: technical review tests passed after remediation; production adoption held.
Reviewed starting commit: 1468a7dc9701053734517ab0af9986050898e3fc.
Scope: candidate reusable information-request preview, BIAN Correspondence 14.0.0 BOM components and TMF681 4.0.0 CommunicationMessage_Create projection.

## Findings and corrections
| Finding reproduced before remediation | Correction | Regression evidence |
| --- | --- | --- |
| Header line breaks and malformed mailbox strings accepted | Reject header controls and require parsed bare mailbox addresses | Header/control and mailbox cases |
| Blank material text and unresolved template tokens accepted | Reject whitespace-only content and unresolved supported placeholder syntax | Material-text and token cases |
| Duplicate recipients accepted across To/Cc | Reject duplicates while preserving local-part case and comparing domain names without case | Duplicate-recipient and preserved-role cases |
| Empty or incomplete source manifest bypassed checks | Require exact coverage of both native schemas and their licences; reject duplicate entries | Empty, missing and duplicate manifest cases |
| Modified source could be accepted after changing its manifest SHA-256 | Verify native publisher blob identity using pins in reviewed verifier code as well as manifest digest and version | Rehashed-source and version cases |
| Caller-supplied schema URI could disagree with selected profile | Bind the reference to the exact selected profile; label the current reference synthetic | Schema-reference and profile-binding cases |
| Malformed JSON-shaped input raised uncontrolled AttributeError | Validate envelope shape before accessing nested fields | Malformed-input cases |
| Duplicate JSON members and missing optional format checkers could weaken validation | Reject duplicate members and fail closed if required format checkers are unavailable | Duplicate-key and missing-checker cases |

These findings concern the review-only preview implementation. No live dispatch endpoint or message send was exercised. The original 23 tests did not cover these cases; a passing earlier suite did not establish readiness.

## Verification
- Fresh virtual environment, Python 3.12.14, declared requirements: **45 unittest methods passed**.
- Existing canonical-envelope script: **13 checks passed** during discovery.
- Publisher schemas retained unchanged; native projections pass the supported structural component checks.
- Sender/recipient roles, content consistency, unknown financial facts, HTML escaping and disabled dispatch verified.
- Changing local approval metadata or an actor authority reference cannot enable dispatch.
- Network calls are blocked in the no-network test; preview succeeds without them.
- Private business application was tested locally; no identifying payload is included in this report or GitHub.
- 25 serial synthetic previews: median 71.63 ms, maximum 98.57 ms on the local test environment.
- 12 previews across four worker threads returned deterministic results.
- A 100-item synthetic request rendered 106,677 bytes and validated.
- These measurements are a bounded local reference exercise, not production capacity or a service-level commitment.
- Machine-readable results: [pre-adoption-20261015.json](evidence/pre-adoption-20261015.json).

## Adoption decision
**Recommendation: retain candidate status and proceed to a controlled integration pilot after semantic review. Production adoption is not established.**

Remaining gates:
1. Allocate/bind canonical profile and schema identities. The current urn:example reference is synthetic.
2. Obtain version-specific enterprise semantic, mapping and renderer approval.
3. Verify native CRM/channel controls, real-party authority and consent, and execution integration.
4. Implement and test durable duplicate-send prevention, response matching, delivery receipts and retries.
5. Select the applicable licensed ACORD insurance artifact, release and separate insurance profile.
6. Establish operational limits and production deployment/release evidence.

The publisher blob pins are trusted only when the verifier code itself is delivered through a reviewed release. Hash checks do not authenticate a wholly modified package. Structural component validation is not full API certification, semantic equivalence, lossless mapping or business approval. Free-text facts and confidentiality require source review.

No merge, adoption, production deployment, live message dispatch or governed business-register change is authorised by this test assessment.
