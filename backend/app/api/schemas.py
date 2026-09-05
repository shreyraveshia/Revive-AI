from __future__ import annotations

from pydantic import BaseModel, Field


class RecoveryDecisionRequest(BaseModel):
    transaction_id: str
    amount_paise: int = Field(gt=0)
    payment_method: str
    failure_code: str

    attempt_number: int = Field(default=1, ge=1)

    customer_previous_transactions: int = Field(default=0, ge=0)
    customer_previous_success_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )
    customer_previous_avg_amount_paise: float = Field(
        default=0.0,
        ge=0.0,
    )

    merchant_previous_transactions: int = Field(default=0, ge=0)
    merchant_previous_success_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )
    merchant_previous_avg_amount_paise: float = Field(
        default=0.0,
        ge=0.0,
    )


class RecoveryDecisionResponse(BaseModel):
    transaction_id: str
    recovery_action_id: str
    selected_action: str
    decision_reason: str
    diagnosis: dict
    action_scores: list[dict]


class RecoveryExecutionRequest(BaseModel):
    recovery_action_id: str
    amount_paise: int = Field(gt=0)
    reference_id: str = Field(min_length=1, max_length=40)
    description: str = Field(min_length=1)
    customer_name: str | None = None
    customer_email: str | None = None


class DemoFailedPaymentRequest(BaseModel):
    amount_paise: int = Field(default=250000, gt=0)
    payment_method: str = "upi"
    failure_code: str = "checkout_abandoned"



class DemoFailedPaymentResponse(BaseModel):
    transaction_id: str
    order_id: str
    amount_paise: int
    payment_method: str
    failure_code: str
    attempt_number: int

    customer_previous_transactions: int
    customer_previous_success_rate: float
    customer_previous_avg_amount_paise: float

    merchant_previous_transactions: int
    merchant_previous_success_rate: float
    merchant_previous_avg_amount_paise: float