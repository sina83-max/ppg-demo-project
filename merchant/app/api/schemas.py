"""Pydantic schemas for the merchant's own public API.

Routers use these for request validation and response shaping only.
Field names for PPG payloads are camelCase (see docs/api-contracts.md);
PPG-facing DTOs are built in the service layer, not here.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class PurchaseStateOut(StrEnum):
    """States returned by the merchant API (mirrors `models.purchase.PurchaseState`)."""

    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    READY_TO_VERIFY = "READY_TO_VERIFY"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    REVERSED = "REVERSED"
    UNKNOWN = "UNKNOWN"
    MANUALLY_SUCCESS = "MANUALLY_SUCCESS"


class PurchaseBase(BaseModel):
    """Common purchase fields for request/response schemas."""

    client_reference_number: str = Field(
        ..., min_length=1, max_length=64, description="Unique merchant reference."
    )
    amount: int = Field(..., gt=0, description="Amount in IRR.")
    wage: int = Field(0, ge=0, description="Wage in IRR.")
    currency: str = Field("IRR", description="Always IRR in this project.")
    description: Optional[str] = None
    user_identifier: Optional[str] = None


class PurchaseCreate(PurchaseBase):
    """Body of `POST /purchases` (form or JSON).

    Note:
        `callbackUrl` is not accepted here; the service builds it from
        `MERCHANT_CALLBACK_BASE`.
    """


class PurchaseRead(PurchaseBase):
    """A local purchase as returned by the JSON API and dashboard."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    purchase_id: Optional[int] = None
    state: PurchaseStateOut
    callback_url: str
    psp_switching_url: Optional[str] = None
    psp_name: Optional[str] = None
    psp_reference_number: Optional[str] = None
    psp_rrn: Optional[str] = None
    payer_masked_card: Optional[str] = None
    fail_reason: Optional[str] = None
    raw_callback: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    verified_at: Optional[datetime] = None


class PurchaseList(BaseModel):
    """Paginated list of local purchases."""

    items: list[PurchaseRead] = []
    total: int = 0


class CallbackResult(BaseModel):
    """Response of `POST /callback`."""

    ok: bool = True
    matched: bool = False
    purchase_id: Optional[int] = None
    state: Optional[PurchaseStateOut] = None


class ActionResult(BaseModel):
    """Generic result for verify / reverse / refresh actions."""

    ok: bool = True
    purchase: Optional[PurchaseRead] = None
    ppg_response: Optional[dict[str, Any]] = None
    error: Optional[str] = None
