from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.executor.base import RecoveryExecutor
from app.executor.schemas import ExecutionResult


class RazorpayExecutor(RecoveryExecutor):
    """Execute supported recovery actions through Razorpay APIs."""

    BASE_URL = "https://api.razorpay.com/v1"

    def __init__(self) -> None:
        settings = get_settings()

        self.key_id = settings.razorpay_key_id
        self.key_secret = settings.razorpay_key_secret

    def execute(
        self,
        *,
        action: str,
        transaction_id: str,
        amount_paise: int,
        reference_id: str,
        description: str,
        customer_name: str | None = None,
        customer_email: str | None = None,
    ) -> ExecutionResult:

        if action == "retry":
            return ExecutionResult(
                success=True,
                action=action,
                external_reference=None,
                customer_url=None,
                message=(
                    "Retry action recorded as simulation; "
                    "no unsupported Razorpay retry API was invoked."
                ),
            )

        if action == "no_action":
            return ExecutionResult(
                success=True,
                action=action,
                external_reference=None,
                customer_url=None,
                message="No recovery action executed.",
            )

        if action == "payment_link":
            return self.create_payment_link(
                amount_paise=amount_paise,
                reference_id=reference_id,
                description=description,
                customer_name=customer_name,
                customer_email=customer_email,
            )

        return ExecutionResult(
            success=False,
            action=action,
            external_reference=None,
            customer_url=None,
            message=(
                f"Action '{action}' does not have an executor "
                "implementation yet."
            ),
        )

    def create_payment_link(
        self,
        *,
        amount_paise: int,
        reference_id: str,
        description: str,
        customer_name: str | None = None,
        customer_email: str | None = None,
    ) -> ExecutionResult:

        if not self.key_id or not self.key_secret:
            raise ValueError(
                "Razorpay credentials are required for PAYMENT_LINK."
            )

        if amount_paise <= 0:
            raise ValueError(
                "Payment link amount must be greater than zero."
            )

        if len(reference_id) > 40:
            raise ValueError(
                "Payment link reference_id must be 40 characters or fewer."
            )

        payload: dict[str, object] = {
            "amount": amount_paise,
            "currency": "INR",
            "reference_id": reference_id,
            "description": description,
            "accept_partial": False,
            "reminder_enable": False,
        }

        customer: dict[str, str] = {}

        if customer_name:
            customer["name"] = customer_name

        if customer_email:
            customer["email"] = customer_email

        if customer:
            payload["customer"] = customer

        response = httpx.post(
            f"{self.BASE_URL}/payment_links",
            json=payload,
            auth=(self.key_id, self.key_secret),
            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        return ExecutionResult(
            success=True,
            action="payment_link",
            external_reference=data.get("id"),
            customer_url=data.get("short_url"),
            message="Razorpay Payment Link created successfully.",
        )