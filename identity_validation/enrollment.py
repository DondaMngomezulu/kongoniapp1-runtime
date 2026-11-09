"""Pure CRM projection and access-gate state machine.

Never treats document verification as acceptance of terms or authorization to issue PINs.
No external side effects. Intended for adapter integration after independent review.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from identity_validation.validator import Status


class EnrollmentState(str, Enum):
    DOCUMENT_PENDING = "DOCUMENT_PENDING"
    IDENTITY_REVIEW = "IDENTITY_REVIEW"
    TERMS_PENDING = "TERMS_PENDING"
    ACCESS_APPROVAL_PENDING = "ACCESS_APPROVAL_PENDING"
    ACCESS_PROVISIONING_PENDING = "ACCESS_PROVISIONING_PENDING"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class EnrollmentEvidence:
    identity_status: Status
    enterprise_terms_accepted: bool
    access_terms_accepted: bool
    access_approved: bool
    slot_approved: bool
    keypad_programmed: bool
    delivery_confirmed: bool
    code_expired: bool = False


def derive_state(e: EnrollmentEvidence) -> EnrollmentState:
    if e.identity_status == Status.REJECTED:
        return EnrollmentState.REJECTED
    if e.identity_status != Status.VERIFIED:
        return EnrollmentState.IDENTITY_REVIEW
    if not (e.enterprise_terms_accepted and e.access_terms_accepted):
        return EnrollmentState.TERMS_PENDING
    if not (e.access_approved and e.slot_approved):
        return EnrollmentState.ACCESS_APPROVAL_PENDING
    if not (e.keypad_programmed and e.delivery_confirmed) or e.code_expired:
        return EnrollmentState.ACCESS_PROVISIONING_PENDING
    return EnrollmentState.ACTIVE


def crm_projection(e: EnrollmentEvidence) -> dict[str, str]:
    """Proposed field values; requires CRM schema validation before write-back."""
    return {
        "ID_Verification_Status": e.identity_status.value,
        "Onboarding_State": derive_state(e).value,
    }
