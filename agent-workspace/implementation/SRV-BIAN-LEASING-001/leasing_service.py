from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, datetime, timezone
from typing import Dict, Any
import uuid


class LeasingError(ValueError):
    pass


@dataclass
class LeasingFacility:
    leasing_id: str
    customer_ref: str
    asset_refs: list[str]
    currency: str
    effective_date: str
    maturity_date: str
    facility_status: str = "INITIATED"
    offer_ref: str | None = None
    agreement_ref: str | None = None
    accounting_refs: list[str] | None = None
    created_at: str = ""
    updated_at: str = ""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_initiate(payload: Dict[str, Any]) -> None:
    required = ["customer_ref", "asset_refs", "currency", "effective_date", "maturity_date", "correlation_id", "idempotency_key"]
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise LeasingError(f"missing required fields: {', '.join(missing)}")
    if not isinstance(payload["asset_refs"], list) or not payload["asset_refs"]:
        raise LeasingError("asset_refs must be a non-empty array")
    if len(str(payload["currency"])) != 3:
        raise LeasingError("currency must be ISO-4217 alpha-3")
    if date.fromisoformat(payload["maturity_date"]) <= date.fromisoformat(payload["effective_date"]):
        raise LeasingError("maturity_date must be later than effective_date")


def initiate(payload: Dict[str, Any]) -> Dict[str, Any]:
    validate_initiate(payload)
    now = _utc_now()
    facility = LeasingFacility(
        leasing_id=str(uuid.uuid4()),
        customer_ref=payload["customer_ref"],
        asset_refs=payload["asset_refs"],
        currency=payload["currency"].upper(),
        effective_date=payload["effective_date"],
        maturity_date=payload["maturity_date"],
        offer_ref=payload.get("offer_ref"),
        agreement_ref=payload.get("agreement_ref"),
        accounting_refs=payload.get("accounting_refs", []),
        created_at=now,
        updated_at=now,
    )
    return asdict(facility)


def retrieve(store: Dict[str, Dict[str, Any]], leasing_id: str) -> Dict[str, Any]:
    if leasing_id not in store:
        raise LeasingError("leasing facility not found")
    return dict(store[leasing_id])


def update(store: Dict[str, Dict[str, Any]], leasing_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    if leasing_id not in store:
        raise LeasingError("leasing facility not found")
    forbidden = {"leasing_id", "created_at", "customer_ref", "currency"}
    if forbidden.intersection(patch):
        raise LeasingError("attempt to modify immutable or authority-controlled fields")
    allowed = {"facility_status", "offer_ref", "agreement_ref", "asset_refs", "maturity_date", "accounting_refs"}
    unknown = set(patch) - allowed
    if unknown:
        raise LeasingError(f"unsupported update fields: {', '.join(sorted(unknown))}")
    current = dict(store[leasing_id])
    current.update(patch)
    current["updated_at"] = _utc_now()
    if date.fromisoformat(current["maturity_date"]) <= date.fromisoformat(current["effective_date"]):
        raise LeasingError("maturity_date must be later than effective_date")
    return current
