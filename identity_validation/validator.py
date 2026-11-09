"""Fail-closed, dependency-free validation primitives for onboarding (Issue #76).

This module does NOT verify a person's identity or document authenticity.
Do not use these results to activate CRM or physical access.
"""
from __future__ import annotations
from datetime import date
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import re


class Status(str, Enum):
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    VERIFIED = "VERIFIED"


@dataclass(frozen=True)
class ValidationResult:
    status: Status
    checks: dict[str, bool]
    reason: str


def _luhn(value: str) -> bool:
    total = 0
    for i, char in enumerate(reversed(value)):
        digit = int(char)
        if i % 2:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def validate_sa_id(number: str) -> ValidationResult:
    """Validate structural plausibility only; never assert authoritative identity."""
    if not isinstance(number, str) or re.fullmatch(r"[0-9]{13}", number) is None:
        return ValidationResult(Status.REJECTED, {"format": False}, "invalid_format")
    yy, mm, dd = int(number[:2]), int(number[2:4]), int(number[4:6])
    today = date.today()
    dates = []
    for century in (1900, 2000):
        try:
            d = date(century + yy, mm, dd)
            if d <= today and (today.year - d.year) <= 125:
                dates.append(d)
        except ValueError:
            pass
    checks = {
        "format": True,
        "plausible_birth_date": bool(dates),
        "citizenship_digit": number[10] in "01",
        "checksum": _luhn(number),
    }
    if not all(checks.values()):
        return ValidationResult(Status.REJECTED, checks, "structural_validation_failed")
    return ValidationResult(
        Status.MANUAL_REVIEW_REQUIRED, checks,
        "structurally_valid_only_authoritative_verification_required"
    )


def intake_key(secret: bytes, document_bytes: bytes, contact_id: str) -> str:
    """Privacy-preserving deterministic key for retry deduplication."""
    if not secret or not document_bytes or not contact_id:
        raise ValueError("secret, document and contact_id required")
    digest = hashlib.sha256(document_bytes).digest()
    return hmac.new(secret, contact_id.encode() + b":" + digest, hashlib.sha256).hexdigest()


def decision(
    structural: ValidationResult,
    authoritative_match: bool | None,
    document_authenticity: bool | None,
    crm_match: bool | None,
) -> ValidationResult:
    """Only verified if all independent required controls pass.

    Caller must validate provenance of authoritative results, consent and freshness.
    """
    checks = dict(structural.checks)
    checks.update({
        "authoritative_match": authoritative_match is True,
        "document_authenticity": document_authenticity is True,
        "crm_match": crm_match is True,
    })
    if structural.status == Status.REJECTED or False in (
        authoritative_match, document_authenticity, crm_match
    ):
        return ValidationResult(Status.REJECTED, checks, "failed_required_check")
    if structural.status != Status.MANUAL_REVIEW_REQUIRED or None in (authoritative_match, document_authenticity, crm_match):
        return ValidationResult(Status.MANUAL_REVIEW_REQUIRED, checks, "incomplete_evidence")
    return ValidationResult(Status.VERIFIED, checks, "all_required_checks_passed")
