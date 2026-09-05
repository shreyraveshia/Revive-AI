from __future__ import annotations

from pydantic import BaseModel, Field


class RecoveryDecisionRequest(BaseModel):
    transaction_id: str
    amount_paise: int = Field(gt=0)

    payment_method: str
    failure_code: str
    attempt_number: int = Field(default=1, ge=1)

    customer_previous_transactions: int = Field(
        default=0,
        ge=0,
    )
    customer_previous_success_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )
    customer_previous_avg_amount_paise: float = Field(
        default=0.0,
        ge=0.0,
    )

    merchant_previous_transactions: int = Field(
        default=0,
        ge=0,
    )
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