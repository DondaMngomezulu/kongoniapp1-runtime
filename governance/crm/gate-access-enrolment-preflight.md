# Gate-access enrolment API contract 1.2

The existing native CRM function `kg_gate_access_enrolment_preflight_v1` remains
a read-only contract publisher with REST disabled. Its source is the adjacent
`.ds` file. Version 1.2 adds explicit CRM Terms of Use acceptance by reply email;
it does not connect an event handler, issue a code or activate a controller.

The four `AccessEntitlements` acceptance fields must be read from CRM at request
time. The required terms reference comes from the server's governed policy, not
from the caller. Resolve the linked Contact and its `CRM_User_ID`, then fetch the
active, confirmed CRM user. Fetch the outgoing terms request and original reply
through the authenticated mail adapter. Normalise the reply's RFC In-Reply-To
reference to the fetched request's provider message ID. A matching thread alone
is insufficient. Verify the recipient, sender, subject identity, terms reference,
message references and timestamps against an authorised human acceptance review.
Resolve `issuerEmail` from the server's authorised sending-mailbox configuration
and verify the request sender against it; do not take it from the HTTP caller.
Do not infer agreement from keywords, quoted content, delivery or read receipts.

`assessAccessCodeTerms({entitlementId}, adapters)` accepts only the record ID.
All other input properties, including caller-supplied acceptance booleans, are
rejected. `adapters.loadTermsContext` must freshly load the trusted evidence above;
it is an adapter boundary, not an implemented CRM/mail integration. The pure
`crmTermsGate` is not an authentication mechanism and must never receive an HTTP
body as its context. Missing, stale, mismatched or unavailable evidence holds the
request. `TERMS_ACCEPTED` is a terms assessment only: `issueCredential` is always
false in this adapter, and independent enterprise/access/identity/controller
requirements remain in force. The enterprise and access gates independently
check this evidence; employee reconciliation cannot bypass it.

Every eventual CRM write must request
`apply_feature_execution: [{"name":"criteria_validation_rule"}]` and retain
the existing workflow, approval and Blueprint controls. Field presence or this
source merge does not prove universal enforcement for imports, privileged API
callers, workflow after-actions or the physical keypad. Those paths need their
own integration evidence before live issuance is enabled.

Tests use synthetic records only. No email body, identity number, image, PIN,
mail address or evidence reference is returned by the assessment helpers. The
CRM function may be updated independently as a read-only contract; deployment of
the evidence adapter and an issuing endpoint remains separately gated.
