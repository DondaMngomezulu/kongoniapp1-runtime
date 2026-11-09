"""Security-first orchestration for identity document verification.

No document is sent to a third party unless an approved provider adapter is configured.
No CRM or physical access side effects occur in this module.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol
from identity_validation.validator import Status, ValidationResult, validate_sa_id, decision, intake_key

MAX_BYTES = 10 * 1024 * 1024
SUPPORTED = {"SA_ID", "DRIVERS_LICENCE", "DRIVERS_LICENSE"}
MAGIC = {b"%PDF-": "application/pdf", b"\xff\xd8\xff": "image/jpeg", b"\x89PNG\r\n\x1a\n": "image/png"}


class Extraction(Protocol):
    def extract(self, content: bytes, mime: str, document_type: str) -> dict[str, str]: ...


class Authority(Protocol):
    def verify(self, *, extracted: dict[str, str], document_type: str, contact_id: str) -> dict[str, object]: ...


@dataclass(frozen=True)
class IntakeResult:
    status: Status
    reason: str
    document_type: str
    idempotency_key: str
    evidence: dict[str, object]


def detect_mime(data: bytes) -> str:
    for signature, mime in MAGIC.items():
        if data.startswith(signature):
            return mime
    raise ValueError("unsupported_file_signature")


def process_document(
    *, content: bytes, document_type: str, contact_id: str,
    dedupe_secret: bytes, extractor: Extraction | None,
    authority: Authority | None, crm_identity_match: bool | None = None,
    consent_recorded: bool = False,
) -> IntakeResult:
    if document_type not in SUPPORTED:
        raise ValueError("unsupported_document_type")
    if not isinstance(content, bytes) or not content or len(content) > MAX_BYTES:
        raise ValueError("invalid_document_size")
    if not contact_id or not dedupe_secret:
        raise ValueError("missing_required_context")
    mime = detect_mime(content)
    key = intake_key(dedupe_secret, content, contact_id)
    evidence: dict[str, object] = {
        "document_sha256": sha256(content).hexdigest(),
        "mime": mime,
        "file_size": len(content),
        "external_provider_invoked": False,
    }
    if extractor is None:
        return IntakeResult(Status.MANUAL_REVIEW_REQUIRED, "ocr_not_configured", document_type, key, evidence)
    try:
        extracted = extractor.extract(content, mime, document_type)
    except Exception:
        return IntakeResult(Status.MANUAL_REVIEW_REQUIRED, "extraction_failed", document_type, key, evidence)
    if not isinstance(extracted, dict):
        return IntakeResult(Status.MANUAL_REVIEW_REQUIRED, "invalid_extraction", document_type, key, evidence)
    evidence["extracted_fields"] = sorted(extracted.keys())  # never log values
    if document_type == "SA_ID":
        structural = validate_sa_id(extracted.get("id_number", ""))
        evidence["structural_checks"] = structural.checks
        if structural.status == Status.REJECTED:
            return IntakeResult(Status.REJECTED, structural.reason, document_type, key, evidence)
    else:
        # Driver's licence authenticity requires a provider or validated decoder.
        structural = ValidationResult(Status.MANUAL_REVIEW_REQUIRED, {}, "licence_validation_pending")
    if not consent_recorded:
        return IntakeResult(Status.MANUAL_REVIEW_REQUIRED, "consent_not_recorded", document_type, key, evidence)
    if authority is None:
        return IntakeResult(Status.MANUAL_REVIEW_REQUIRED, "authoritative_provider_not_configured", document_type, key, evidence)
    try:
        provider_result = authority.verify(extracted=extracted, document_type=document_type, contact_id=contact_id)
        evidence["external_provider_invoked"] = True
    except Exception:
        return IntakeResult(Status.MANUAL_REVIEW_REQUIRED, "provider_unavailable", document_type, key, evidence)
    # A provider adapter must authenticate responses and enforce freshness, tenant binding,
    # consent scope, source identity and documented result semantics before returning.
    if not isinstance(provider_result, dict) or provider_result.get("evidence_authenticated") is not True:
        return IntakeResult(Status.MANUAL_REVIEW_REQUIRED, "provider_evidence_untrusted", document_type, key, evidence)
    evidence["provider_reference"] = str(provider_result.get("reference", ""))[:128]
    matched = provider_result.get("identity_match")
    authentic = provider_result.get("document_authenticity")
    if type(matched) is not bool:
        matched = None
    if type(authentic) is not bool:
        authentic = None
    result = decision(structural, matched, authentic, crm_identity_match)
    # A licence needs a dedicated validated document authenticity check from the provider.
    return IntakeResult(result.status, result.reason, document_type, key, evidence)
