# Universal UBL 2.5 HTML email and Mail Merge projections (candidate)

The 101 UBL 2.5 main-document types receive exactly one candidate projection key each. Based on 93 preserved UBL 2.4 register identifiers, eight names require new governed ID allocation: DeliveryNote, InvoiceStatusRequest, InvoiceStatusResponse, ProcurementStatus, ProcurementStatusRequest, WasteMovement, WasteNotification, WorkReport.

Architecture: canonical UBL XML is verified through the appropriate schema and applicable business rules; HTML/text/plain are presentation views only. Mail Merge data must be typed, escaped and sourced from approved CRM/entity/derived fields. Send only through CRM-authorised workflow; Gmail is transport. Every rendered document retains source ID, template version, XML instance hash, issuer and CRM correspondence audit correlation.

Policies: EMAIL_PRIMARY is primarily a human readable message while canonical XML continues where required. EMAIL_WITH_CANONICAL_DOCUMENT includes the controlled source XML/document; COVERING_EMAIL_ONLY forbids replacing the formal original (e.g. contracts, trade/customs records). All policies are PROPOSED and not sufficient for legal issuance.

MRG-CVR-001 v1.0 applies only to approved -CVR templates and remains unchanged; its parent-document attachment rule cannot be bypassed.

Gate failures and exceptions: UBL 2.5 XSD access/compile/semantics; eight new controlled IDs; 93 prior migrations; unique templates and CRM field mappings; statutory/tax/tender/contract-channel checks; email-safe HTML plus text/plain; unresolved merge slots; attachment/secure-link preservation; proof-of-delivery readback; production authorisation. SB-0002 remains DespatchAdvice; mapping to new DeliveryNote is not automatic.

Source: https://docs.oasis-open.org/ubl/os-UBL-2.5/xsd/maindoc/ ; live inventory https://docs.google.com/spreadsheets/d/1TlHa9Q43Y-xJr-QJN4QveO0TKhT9hwm13K0wpX6BGVI/edit . Counts and names are catalogue coverage, not 101 approved templates, nor end-to-end XSD conformance. Pending issue #52.
