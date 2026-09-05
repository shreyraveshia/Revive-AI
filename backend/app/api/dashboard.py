from sqlalchemy import func, select

from app.domain.enums import RecoveryActionStatus
from app.db.session import SessionLocal
from app.models.recovery_action import RecoveryAction
from app.models.recovery_outcome import RecoveryOutcome
from app.models.transaction import Transaction


def get_metrics():
    with SessionLocal() as db:
        failed_payments = db.scalar(
            select(func.count(Transaction.id)).where(Transaction.status == "failed")
        ) or 0

        revenue_at_risk = db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.status == "failed"
            )
        ) or 0

        recovered_revenue = db.scalar(
            select(func.coalesce(func.sum(RecoveryOutcome.amount_recovered_paise), 0)).where(
                RecoveryOutcome.status == "recovered"
            )
        ) or 0

        executed_actions = db.scalar(
            select(func.count(RecoveryAction.id)).where(
                func.upper(RecoveryAction.status) == "EXECUTED"
            )
        ) or 0

        total_recovery_outcomes = db.scalar(
            select(func.count(RecoveryOutcome.id))
        ) or 0

        recovered_outcomes = db.scalar(
            select(func.count(RecoveryOutcome.id)).where(
                RecoveryOutcome.status == "recovered"
            )
        ) or 0

        recovery_rate = (
            recovered_outcomes / total_recovery_outcomes
            if total_recovery_outcomes
            else 0.0
        )

        return {
            "failed_payments": failed_payments,
            "revenue_at_risk_paise": revenue_at_risk,
            "recovered_revenue_paise": recovered_revenue,
            "executed_actions": executed_actions,
            "recovery_rate": recovery_rate,
        }


def get_recovery_actions(limit: int = 50):
    with SessionLocal() as db:
        rows = db.execute(
            select(
                RecoveryAction,
                Transaction.amount,
                Transaction.order_id,
                Transaction.status.label("transaction_status"),
            )
            .join(
                Transaction,
                RecoveryAction.transaction_id == Transaction.id,
            )
            .order_by(RecoveryAction.created_at.desc())
            .limit(limit)
        ).all()

        return [
            {
                "action_id": action.id,
                "transaction_id": action.transaction_id,
                "order_id": order_id,
                "amount_paise": amount,
                "action": action.action_type,
                "reason": action.decision_reason,
                "expected_recovery_probability": action.expected_recovery_probability,
                "expected_value_paise": action.expected_value_paise,
                "status": action.status,
                "transaction_status": transaction_status,
                "created_at": action.created_at,
                "executed_at": action.executed_at,
            }
            for action, amount, order_id, transaction_status in rows
        ]