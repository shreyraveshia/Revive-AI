from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal
from app.executor.razorpay import RazorpayExecutor
from app.models.recovery_action import RecoveryAction


def execute_payment_link_for_action(
    *,
    recovery_action_id: str,
    amount_paise: int,
    reference_id: str,
    description: str,
    customer_name: str | None = None,
    customer_email: str | None = None,
) -> object:
    """Create a Razorpay Payment Link and persist its external reference."""

    db = SessionLocal()

    try:
        action = db.scalar(
            select(RecoveryAction).where(
                RecoveryAction.id == recovery_action_id
            )
        )

        if action is None:
            raise ValueError(
                f"RecoveryAction not found: {recovery_action_id}"
            )

        if action.external_reference:
            raise ValueError(
                "RecoveryAction already has an external reference."
            )

        executor = RazorpayExecutor()

        result = executor.execute(
            action="payment_link",
            transaction_id=action.transaction_id,
            amount_paise=amount_paise,
            reference_id=reference_id,
            description=description,
            customer_name=customer_name,
            customer_email=customer_email,
        )

        if not result.success:
            raise RuntimeError(result.message)

        action.external_reference = result.external_reference
        action.status = "EXECUTED"

        db.commit()

        return result

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()