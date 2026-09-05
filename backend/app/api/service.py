from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from app.agent.context import RecoveryContext
from app.agent.service import ReviveAgent
from app.executor.service import execute_payment_link_for_action
from app.api.schemas import (
    RecoveryDecisionRequest,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "artifacts" / "recovery_model.joblib"
FEATURE_PATH = PROJECT_ROOT / "artifacts" / "recovery_features.txt"


def build_agent() -> ReviveAgent:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Recovery model not found: {MODEL_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    feature_columns = FEATURE_PATH.read_text(
        encoding="utf-8"
    ).splitlines()

    return ReviveAgent(
        recovery_model=model,
        feature_columns=feature_columns,
    )


def decide_recovery(
    request: RecoveryDecisionRequest,
):
    agent = build_agent()

    context = RecoveryContext(
        transaction_id=request.transaction_id,
        amount_paise=request.amount_paise,
        payment_method=request.payment_method,
        failure_code=request.failure_code,
        attempt_number=request.attempt_number,
        customer_previous_transactions=(
            request.customer_previous_transactions
        ),
        customer_previous_success_rate=(
            request.customer_previous_success_rate
        ),
        customer_previous_avg_amount_paise=(
            request.customer_previous_avg_amount_paise
        ),
        merchant_previous_transactions=(
            request.merchant_previous_transactions
        ),
        merchant_previous_success_rate=(
            request.merchant_previous_success_rate
        ),
        merchant_previous_avg_amount_paise=(
            request.merchant_previous_avg_amount_paise
        ),
    )

    return agent.decide(context)


def execute_recovery_payment_link(
    *,
    recovery_action_id: str,
    amount_paise: int,
    reference_id: str,
    description: str,
    customer_name: str | None,
    customer_email: str | None,
):
    return execute_payment_link_for_action(
        recovery_action_id=recovery_action_id,
        amount_paise=amount_paise,
        reference_id=reference_id,
        description=description,
        customer_name=customer_name,
        customer_email=customer_email,
    )