from __future__ import annotations

from pydantic import BaseModel


class ExecutionResult(BaseModel):
    success: bool
    action: str
    external_reference: str | None = None
    customer_url: str | None = None
    message: str


class PaymentLinkRequest(BaseModel):
    amount_paise: int
    reference_id: str
    description: str
    customer_name: str | None = None
    customer_email: str | None = None