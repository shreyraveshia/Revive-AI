from __future__ import annotations

from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.domain.enums import RecoveryActionStatus
from app.executor.razorpay import RazorpayExecutor
from app.executor.schemas import PaymentLinkRequest
from app.models.recovery_action import RecoveryAction


def execute_payment_link_for_action(
    recovery_action_id: str,
    amount_paise: int,
    reference_id: str,
    description: str,
    customer_name: str | None = None,
    customer_email: str | None = None,
):
    """
    Execute a Payment Link for an existing RecoveryAction.

    The RecoveryAction acts as the durable audit/idempotency boundary.
    A Payment Link cannot be created again once an external reference
    has already been recorded for the action.
    """

    with SessionLocal() as db:
        recovery_action = db.get(
            RecoveryAction,
            recovery_action_id,
        )

        if recovery_action is None:
            raise ValueError(
                f"RecoveryAction not found: {recovery_action_id}"
            )

        if recovery_action.external_reference:
            raise ValueError(
                "RecoveryAction already has an external reference."
            )

        if recovery_action.action_type != "payment_link":
            raise ValueError(
                f"RecoveryAction is for "
                f"'{recovery_action.action_type}', "
                f"not 'payment_link'."
            )

        request = PaymentLinkRequest(
            amount_paise=amount_paise,
            currency="INR",
            reference_id=reference_id,
            description=description,
            customer_name=customer_name,
            customer_email=customer_email,
        )

        executor = RazorpayExecutor()

        result = executor.create_payment_link(request)

        if not result.success:
            return result

        recovery_action.external_reference = result.external_reference
        recovery_action.status = RecoveryActionStatus.EXECUTED
        recovery_action.executed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(recovery_action)

        return result