# Full UBL 2.5 XML -> HTML and Plain-text Projection Suite

101 XSLT HTML templates and 101 XSLT plain-text templates are bound to 101 normative OASIS UBL 2.5 document type roots, plus 2 shared rendering stylesheets and a one-to-one candidate index. All source content is generic canonical XML structure; it is NOT 101 individually approved business-formatted document templates.

Two modes: DOCUMENT renders structured fields, nested parties, repeated lines and attributes for all 101 types. EMAIL renders structured fields except when policy is COVERING_EMAIL_ONLY; that email shows document identity and sends **no** detailed content. Formal original and required portal/attachment remain required. HTML and text/plain are MIME alternatives.

The renderer checks root namespace and document type. A full validation adapter must validate OASIS normative XSD and business rules **before** rendering or any communication. No sender/recipient/system data in this repository.

Shared source: `templates/full/shared/`. Each type-specific stylesheet: `templates/full/by-type/<Type>.{html,text}.xsl`. Registry: `full-template-projection-index.candidate.json`.

Issue restrictions from adopted MRG-CVR-001 v1.0: no unresolved placeholders; parent template published; covering email always includes rendered parent document; issuing contracting group entity only; verified banking details only; mandatory Received/Durban availability block for quotes/lease offers to leads. Existing -CVR contract unchanged; these XSLTs never authorise sends.

Additional gates: XML Schema/Schematron conformance, CRM field/party/role mapping, real instance tests, issuer/channel/legal/tax review, actual CRM drafts and human-readable rendering, audit readback, native app acceptance. All 101 send_enabled=false, HIT CHECK_STUDY_HOLD.
