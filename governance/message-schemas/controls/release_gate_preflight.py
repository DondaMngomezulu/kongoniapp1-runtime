"""Pure preflight evaluation for AI-NATIVE-ISSUE-SEND-001. REVIEW ONLY.

This module does NOT verify approval signatures, source authenticity, authorisation or
live CRM state, and MUST NOT be used to authorise a production send.
"""
from datetime import datetime, timezone

DOCUMENT_INTENTS = {
    "QUOTATION", "FINANCE_LEASE", "OPERATING_LEASE", "AGREEMENT",
    "INVOICE", "ORDER", "DELIVERY_NOTE", "WARRANTY", "LEGAL_NOTICE"
}
FINANCE_INTENTS = {"FINANCE_LEASE", "OPERATING_LEASE"}
QUOTATION_INTENTS = {"QUOTATION", "FINANCE_LEASE", "OPERATING_LEASE"}


def assess_candidate(payload, trusted=None, now=None):
    """Return DENY or REVIEW_ONLY; never return an authority to send.

    trusted must be supplied from a different independently authenticated service.
    A caller supplying its own evidence does not authenticate it.
    """
    reasons = []
    trusted = trusted or {}
    now = now or datetime.now(timezone.utc)
    template = payload.get("template") or {}
    parent = payload.get("parent")
    issuer = payload.get("issuer") or {}
    approval = payload.get("approval") or {}
    snapshot = payload.get("snapshot") or {}
    crm = payload.get("crm") or {}
    channel = payload.get("channel")
    intent = payload.get("intent")
    recipients = payload.get("recipients") or []


    basis = payload.get("issuance_basis")
    specific = payload.get("specific_approval")
    message_hash = snapshot.get("message_hash")
    if not intent or intent not in template.get("allowed_intents", []):
        reasons.append("INTENT_NOT_GOVERNED")
    if basis not in ("GOVERNED_TEMPLATE", "APPROVED_SPECIFIC_TEMPLATE"):
        reasons.append("ISSUANCE_BASIS_INVALID")
    if not message_hash or approval.get("message_hash") != message_hash:
        reasons.append("MESSAGE_NOT_APPROVED")
    if not trusted.get("message_hash_verified"):
        reasons.append("MESSAGE_HASH_UNVERIFIED")
    if not trusted.get("exact_template_scope_verified"):
        reasons.append("TEMPLATE_SCOPE_UNVERIFIED")
    expected = {
        "intent": intent, "channel": channel, "action": payload.get("action"),
        "issuer_id": issuer.get("entity_id"), "crm_record_id": crm.get("record_id"),
        "template_id": template.get("id"), "template_hash": template.get("hash")}
    for field, value in expected.items():
        if not value or approval.get(field) != value:
            reasons.append("APPROVAL_SCOPE_" + field.upper())
    if not recipients or len(recipients) != len(set(recipients)) or sorted(recipients) != sorted(approval.get("recipients") or []):
        reasons.append("APPROVAL_RECIPIENTS_MISMATCH")
    if intent in DOCUMENT_INTENTS:
        if not snapshot.get("parent_instance_hash"):
            reasons.append("PARENT_INSTANCE_MISSING")
        if approval.get("parent_instance_hash") != snapshot.get("parent_instance_hash"):
            reasons.append("PARENT_INSTANCE_CHANGED")
        if not trusted.get("parent_instance_verified"):
            reasons.append("PARENT_INSTANCE_UNVERIFIED")
    if basis == "APPROVED_SPECIFIC_TEMPLATE":
        if not isinstance(specific, dict) or specific.get("status") != "APPROVED":
            reasons.append("SPECIFIC_TEMPLATE_NOT_APPROVED")
        else:
            scoped = {
                "template_id": template.get("id"), "template_version": template.get("version"),
                "template_hash": template.get("hash"), "issuer_id": issuer.get("entity_id"),
                "crm_record_id": crm.get("record_id"), "channel": channel,
                "intent": intent, "message_hash": message_hash}
            for field, value in scoped.items():
                if not value or specific.get(field) != value:
                    reasons.append("SPECIFIC_SCOPE_" + field.upper())
            if sorted(specific.get("recipients") or []) != sorted(recipients):
                reasons.append("SPECIFIC_RECIPIENTS_MISMATCH")
            try:
                expiry_specific = datetime.fromisoformat(specific.get("expires_at","").replace("Z","+00:00"))
                if expiry_specific.tzinfo is None or expiry_specific <= now:
                    reasons.append("SPECIFIC_APPROVAL_EXPIRED")
            except (ValueError,TypeError,AttributeError):
                reasons.append("SPECIFIC_APPROVAL_EXPIRY_INVALID")
            if not specific.get("receipt") or not trusted.get("specific_approval_verified"):
                reasons.append("SPECIFIC_APPROVAL_UNVERIFIED")
    elif specific is not None:
        reasons.append("UNEXPECTED_SPECIFIC_APPROVAL")

    if not trusted.get("independently_authenticated"):
        reasons.append("TRUSTED_EVIDENCE_MISSING")
    if template.get("status") != "CONTROLLED":
        reasons.append("TEMPLATE_NOT_CONTROLLED")
    if channel not in template.get("channels", []):
        reasons.append("CHANNEL_MISMATCH")
    if template.get("issuer_id") != issuer.get("entity_id"):
        reasons.append("TEMPLATE_ISSUER_MISMATCH")
    if not template.get("approval_receipt"):
        reasons.append("TEMPLATE_APPROVAL_MISSING")
    if intent in DOCUMENT_INTENTS:
        if not isinstance(parent, dict):
            reasons.append("PARENT_REQUIRED")
        else:
            if parent.get("status") != "CONTROLLED":
                reasons.append("PARENT_NOT_CONTROLLED")
            if parent.get("issuer_id") != issuer.get("entity_id"):
                reasons.append("PARENT_ISSUER_MISMATCH")
            if not parent.get("approval_receipt"):
                reasons.append("PARENT_APPROVAL_MISSING")
    if snapshot.get("merge_status") != "PASS":
        reasons.append("MERGE_INCOMPLETE")
    if approval.get("status") != "APPROVED":
        reasons.append("RELEASE_NOT_APPROVED")
    if snapshot.get("source_hash") != approval.get("source_hash"):
        reasons.append("SOURCE_CHANGED")
    if snapshot.get("artifact_hash") != approval.get("artifact_hash"):
        reasons.append("ARTIFACT_CHANGED")
    try:
        expiry = datetime.fromisoformat(approval.get("expires_at", "").replace("Z", "+00:00"))
        if expiry.tzinfo is None or expiry <= now:
            reasons.append("APPROVAL_EXPIRED")
    except (ValueError, TypeError):
        reasons.append("APPROVAL_EXPIRY_INVALID")
    if not recipients:
        reasons.append("RECIPIENT_MISSING")
    if not trusted.get("recipient_authorised"):
        reasons.append("RECIPIENT_NOT_VERIFIED")
    if not trusted.get("sender_authorised"):
        reasons.append("SENDER_NOT_VERIFIED")
    if not trusted.get("source_hash_verified"):
        reasons.append("SOURCE_RECEIPT_UNVERIFIED")
    if not trusted.get("template_hash_verified"):
        reasons.append("TEMPLATE_HASH_UNVERIFIED")
    if intent in DOCUMENT_INTENTS and not trusted.get("parent_hash_verified"):
        reasons.append("PARENT_HASH_UNVERIFIED")
    if intent in QUOTATION_INTENTS and not trusted.get("availability_verified"):
        reasons.append("AVAILABILITY_UNVERIFIED")
    if intent in FINANCE_INTENTS and not trusted.get("credit_approval_verified"):
        reasons.append("CREDIT_UNVERIFIED")
    if intent in QUOTATION_INTENTS and not trusted.get("pricing_verified"):
        reasons.append("PRICE_UNVERIFIED")
    if not trusted.get("crm_record_current"):
        reasons.append("CRM_STATE_UNVERIFIED")
    if trusted.get("account_quote_blocked") and intent in QUOTATION_INTENTS:
        reasons.append("ACCOUNT_QUOTE_HOLD")
    if not trusted.get("channel_access_control_verified"):
        reasons.append("TRANSPORT_BYPASS_NOT_CLOSED")
    if not trusted.get("idempotency_key_available"):
        reasons.append("DUPLICATE_OR_UNVERIFIED_SEND")
    if not trusted.get("current_exact_approval_verified"):
        reasons.append("LIVE_APPROVAL_UNVERIFIED")
    if not crm.get("account_id") or not crm.get("record_id"):
        reasons.append("CRM_BINDING_MISSING")

    if reasons:
        return {"decision": "DENY", "reason_codes": sorted(set(reasons))}
    return {"decision": "REVIEW_ONLY", "reason_codes": ["PRODUCTION_RELEASE_NOT_IMPLEMENTED"]}
