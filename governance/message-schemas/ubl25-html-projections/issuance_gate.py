"""Strictly advisory, fail-closed UBL issuance gate. It DOES NOT send messages.
The approved runtime and issuer must independently enforce all controls.
"""
def assess(profile, evidence):
    failures=[]
    def need(ok,code):
        if ok is not True:failures.append(code)
    need(profile.get("send_enabled"),"PROFILE_DISABLED")
    need(profile.get("publication")=="APPROVED","TEMPLATE_UNAPPROVED")
    need(profile.get("crm_field_mapping")=="APPROVED","CRM_MAPPING_UNAPPROVED")
    for k in ("canonical_ubl25_xsd_pass","business_rules_pass","parent_document_published","authorised_contracting_entity","crm_issuer_authorised","recipient_verified","no_unresolved_merge_tokens","legal_delivery_channel_approved","audit_retention_authorised","crm_correspondence_readback"):
        need(evidence.get(k),k.upper())
    if evidence.get("recipient_opt_out") is not False:failures.append("RECIPIENT_OPT_OUT_UNKNOWN_OR_TRUE")
    if not evidence.get("canonical_document_sha256"):failures.append("CANONICAL_HASH_REQUIRED")
    if not evidence.get("idempotency_key"):failures.append("IDEMPOTENCY_KEY_REQUIRED")
    policy=profile.get("email_policy")
    if policy not in ("EMAIL_PRIMARY","EMAIL_WITH_CANONICAL_DOCUMENT","COVERING_EMAIL_ONLY"):failures.append("POLICY_INVALID")
    if policy in ("EMAIL_WITH_CANONICAL_DOCUMENT","COVERING_EMAIL_ONLY"):
        need(evidence.get("rendered_parent_document_attached"),"RENDERED_PARENT_ATTACHMENT_REQUIRED")
    if policy=="COVERING_EMAIL_ONLY":
        need(evidence.get("signed_original_or_portal_submission_valid"),"FORMAL_ORIGINAL_OR_PORTAL_EVIDENCE_MISSING")
    if evidence.get("bank_details_included") is True:
        need(evidence.get("verified_proof_of_banking"),"PROOF_OF_BANKING_MISSING")
    if evidence.get("quote_or_lease_offer_to_lead") is True:
        need(evidence.get("durban_port_availability_block_verified"),"DURBAN_AVAILABILITY_BLOCK_MISSING")
    return {"decision":"DENY" if failures else "READY_FOR_INDEPENDENT_ISSUER_APPROVAL","failed_controls":failures}
