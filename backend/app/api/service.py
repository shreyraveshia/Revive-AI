from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

import joblib

from app.agent.context import RecoveryContext
from app.agent.service import ReviveAgent
from app.executor.service import execute_payment_link_for_action
from app.api.schemas import RecoveryDecisionRequest
from app.db.session import SessionLocal
from app.domain.enums import (
    FailureCode,
    PaymentAttemptStatus,
    PaymentMethod,
    RecoveryActionStatus,
    TransactionStatus,
)
from app.models.customer import Customer
from app.models.merchant import Merchant
from app.models.payment_attempt import PaymentAttempt
from app.models.recovery_action import RecoveryAction
from app.models.transaction import Transaction


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "artifacts" / "recovery_model.joblib"
FEATURE_PATH = PROJECT_ROOT / "artifacts" / "recovery_features.txt"


def build_agent() -> ReviveAgent:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Recovery model not found: {MODEL_PATH}")

    model = joblib.load(MODEL_PATH)

    feature_columns = FEATURE_PATH.read_text(
        encoding="utf-8"
    ).splitlines()

    return ReviveAgent(
        recovery_model=model,
        feature_columns=feature_columns,
    )


def decide_recovery(request: RecoveryDecisionRequest):
    agent = build_agent()

    context = RecoveryContext(
        transaction_id=request.transaction_id,
        amount_paise=request.amount_paise,
        payment_method=request.payment_method,
        failure_code=request.failure_code,
        attempt_number=request.attempt_number,
        customer_previous_transactions=request.customer_previous_transactions,
        customer_previous_success_rate=request.customer_previous_success_rate,
        customer_previous_avg_amount_paise=request.customer_previous_avg_amount_paise,
        merchant_previous_transactions=request.merchant_previous_transactions,
        merchant_previous_success_rate=request.merchant_previous_success_rate,
        merchant_previous_avg_amount_paise=request.merchant_previous_avg_amount_paise,
    )

    result = agent.decide(context)

    with SessionLocal() as db:
        transaction = db.get(
            Transaction,
            request.transaction_id,
        )

        if transaction is None:
            raise ValueError(
                f"Transaction not found: {request.transaction_id}"
            )

        selected_score = next(
            score
            for score in result.policy_result.scores
            if score.action == result.policy_result.selected_action
        )

        idempotency_key = (
            f"recovery:{request.transaction_id}:"
            f"{result.policy_result.selected_action}"
        )

        recovery_action = (
            db.query(RecoveryAction)
            .filter(
                RecoveryAction.idempotency_key == idempotency_key
            )
            .first()
        )

        if recovery_action is None:
            recovery_action = RecoveryAction(
                id=str(uuid4()),
                transaction_id=request.transaction_id,
                action_type=result.policy_result.selected_action,
                decision_reason=result.policy_result.reason,
                confidence=result.diagnosis.confidence,
                expected_recovery_probability=selected_score.recovery_probability,
                expected_value_paise=selected_score.expected_value_paise,
                status=RecoveryActionStatus.PROPOSED,
                idempotency_key=idempotency_key,
            )

            db.add(recovery_action)
            db.commit()
            db.refresh(recovery_action)

    return result, recovery_action


def execute_recovery_payment_link(
    recovery_action_id: str,
    amount_paise: int,
    reference_id: str,
    description: str,
    customer_name: str | None = None,
    customer_email: str | None = None,
):
    return execute_payment_link_for_action(
        recovery_action_id=recovery_action_id,
        amount_paise=amount_paise,
        reference_id=reference_id,
        description=description,
        customer_name=customer_name,
        customer_email=customer_email,
    )


def create_demo_failed_payment(
    amount_paise: int = 250000,
    payment_method: str = "upi",
    failure_code: str = "checkout_abandoned",
):
    transaction_id = str(uuid4())
    order_id = f"REVIVE-DEMO-{uuid4().hex[:12].upper()}"

    payment_method = PaymentMethod(payment_method)
    failure_code = FailureCode(failure_code)

    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        merchant = (
            db.query(Merchant)
            .filter(
                Merchant.name == "Revive Demo Merchant"
            )
            .first()
        )

        if merchant is None:
            merchant = Merchant(
                id=str(uuid4()),
                name="Revive Demo Merchant",
                category="online_retail",
            )
            db.add(merchant)
            db.flush()

        customer = (
            db.query(Customer)
            .filter(
                Customer.email == "revive-demo@example.com"
            )
            .first()
        )

        if customer is None:
            customer = Customer(
                id=str(uuid4()),
                merchant_id=merchant.id,
                name="Demo Customer",
                email="revive-demo@example.com",
            )
            db.add(customer)
            db.flush()

        transaction = Transaction(
            id=transaction_id,
            merchant_id=merchant.id,
            customer_id=customer.id,
            order_id=order_id,
            amount=amount_paise,
            currency="INR",
            status=TransactionStatus.FAILED,
            created_at=now,
        )

        db.add(transaction)
        db.flush()

        payment_attempt = PaymentAttempt(
            id=str(uuid4()),
            transaction_id=transaction.id,
            attempt_number=1,
            payment_method=payment_method,
            gateway="razorpay",
            status=PaymentAttemptStatus.FAILED,
            failure_code=failure_code,
            created_at=now,
        )

        db.add(payment_attempt)
        db.commit()

    return {
        "transaction_id": transaction_id,
        "order_id": order_id,
        "amount_paise": amount_paise,
        "payment_method": payment_method,
        "failure_code": failure_code,
        "attempt_number": 1,
        "customer_previous_transactions": 8,
        "customer_previous_success_rate": 0.67,
        "customer_previous_avg_amount_paise": 210000.0,
        "merchant_previous_transactions": 120,
        "merchant_previous_success_rate": 0.91,
        "merchant_previous_avg_amount_paise": 195000.0,
    }