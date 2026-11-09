"""Safe CRM transition planning, without side effects or secrets.

This is an adapter boundary, NOT a Zoho CRM connector. The caller must supply
fresh authoritative CRM state and persist changes with optimistic concurrency.
"""
from __future__ import annotations
from dataclasses import dataclass
from identity_validation.enrollment import EnrollmentEvidence, derive_state
from identity_validation.validator import Status

ALLOWED_STATUS = frozenset(s.value for s in Status)


@dataclass(frozen=True)
class CRMUpdatePlan:
    contact_id: str
    expected_version: str
    fields: dict[str, str]
    requires_review: bool


def plan_contact_update(
    *,
    contact_id: str,
    expected_version: str,
    evidence: EnrollmentEvidence,
    current_identity_status: str,
    existing_identity_verified: bool = False,
) -> CRMUpdatePlan:
    """Fail closed; do not silently downgrade a previously verified record.

    Never writes to CRM, issues a PIN, or assumes a field exists.
    """
    if not contact_id or not expected_version:
        raise ValueError("contact_id and expected_version required")
    if current_identity_status not in ALLOWED_STATUS:
        raise ValueError("unknown_current_identity_status")
    if existing_identity_verified or current_identity_status == Status.VERIFIED.value:
        if evidence.identity_status != Status.VERIFIED:
            raise ValueError("verified_record_requires_manual_reconciliation")
    target = derive_state(evidence)
    return CRMUpdatePlan(
        contact_id=contact_id,
        expected_version=expected_version,
        fields={
            "ID_Verification_Status": evidence.identity_status.value,
            "Onboarding_State": target.value,
        },
        requires_review=(evidence.identity_status != Status.VERIFIED),
    )


def validate_slot(slot: int, *, master_slot: int = 100) -> bool:
    """Candidate employee slot policy; confirmation from live policy required."""
    if isinstance(slot, bool) or not isinstance(slot, int):
        return False
    return 200 <= slot <= 219 and slot != master_slot
