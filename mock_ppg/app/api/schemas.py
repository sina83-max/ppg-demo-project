"""Pydantic schemas mirroring the PPG v3 request/response bodies.

Kept close to the real API (camelCase in, camelCase out) so the merchant
cannot tell the mock from the real gateway.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    """Body of `POST /v3/tokens`."""

    apiKey: str = Field(..., alias="apiKey")
    secretKey: str = Field(..., alias="secretKey")

    model_config = {"populate_by_name": True}


class TokenRefreshRequest(BaseModel):
    """Body of `POST /v3/tokens/refresh`."""

    refreshToken: str = Field(..., alias="refreshToken")

    model_config = {"populate_by_name": True}


class TokenResponse(BaseModel):
    """Response of the token endpoints."""

    accessToken: str
    refreshToken: str
    tokenType: str = "Bearer"
    expiresIn: Optional[int] = 3600


class CreatePurchaseRequest(BaseModel):
    """Body of `POST /v3/purchases` (see docs/api-contracts.md section 3)."""

    amount: int = Field(..., gt=0)
    currency: str = "IRR"
    callbackUrl: str
    clientReferenceNumber: str

    wage: Optional[int] = None
    description: Optional[str] = None
    userIdentifier: Optional[str] = None
    payerMobileNumber: Optional[str] = None
    payerNationalCode: Optional[str] = None
    payerCardNumber: Optional[str] = None
    payerCardNumbers: Optional[list[str]] = None
    additionalData: Optional[dict[str, Any]] = None
    switching: Optional[dict[str, Any]] = None

    model_config = {"populate_by_name": True}


class PurchaseCreationResult(BaseModel):
    """Response of `POST /v3/purchases`."""

    purchaseId: int
    pspSwitchingUrl: str
    clientReferenceNumber: Optional[str] = None
    state: str = "IN_PROGRESS"


class ReverseRequest(BaseModel):
    """Body of `POST /v3/purchases/reverse`."""

    purchaseId: Optional[int] = None
    clientReferenceNumber: Optional[str] = None

    model_config = {"populate_by_name": True}


class VerificationResult(BaseModel):
    """Response of `POST /v3/purchases/{id}/verify`."""

    status: str
    purchaseId: Optional[int] = None
    state: Optional[str] = None
    message: Optional[str] = None


class ReverseResult(BaseModel):
    """Response of `POST /v3/purchases/reverse`."""

    status: str
    purchaseId: Optional[int] = None
    state: Optional[str] = None
    message: Optional[str] = None


class PPGErrorItem(BaseModel):
    """Single entry of the PPG error list (docs/api-contracts.md section 5)."""

    code: str
    message: str


class PPGErrorResponse(BaseModel):
    """Standard PPG error envelope."""

    fingerprint: Optional[str] = None
    errors: list[PPGErrorItem] = []
