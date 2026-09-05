from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FailureDiagnosis(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    likely_cause: str = Field(
        description="Most likely reason for the payment failure."
    )

    severity: str = Field(
        description="Failure severity: low, medium, or high."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the diagnosis."
    )

    explanation: str = Field(
        description="Concise explanation grounded only in supplied context."
    )

    recommended_recovery_focus: str = Field(
        description=(
            "Preferred recovery direction, without executing any action."
        )
    )

    customer_message: str = Field(
        description="A concise customer-facing recovery message."
    )

def build_fallback_diagnosis(
    *,
    failure_code: str,
) -> FailureDiagnosis:
    """
    Build a deterministic fallback diagnosis when the LLM
    is unavailable.

    This does not claim to be an LLM-generated explanation.
    """

    fallback_messages = {
        "upi_timeout": (
            "Your payment timed out. Please try again in a few minutes "
            "or use another payment method."
        ),
        "upi_declined": (
            "Your UPI payment was declined. Please try another payment method."
        ),
        "insufficient_funds": (
            "Your payment could not be completed. Please check your "
            "available balance or use another payment method."
        ),
        "hard_decline": (
            "Your card payment could not be completed. "
            "Please try another payment method."
        ),
        "soft_decline": (
            "Your payment could not be completed right now. "
            "Please try again or use another payment method."
        ),
        "network_error": (
            "We couldn't complete the payment because of a temporary "
            "network issue. Please try again shortly."
        ),
        "gateway_error": (
            "We couldn't complete the payment because of a temporary "
            "payment service issue. Please try again shortly."
        ),
        "authentication_failed": (
            "The payment could not be authenticated. "
            "Please retry or use another payment method."
        ),
        "checkout_abandoned": (
            "It looks like your checkout was not completed. "
            "You can continue your payment using the available payment link."
        ),
    }

    message = fallback_messages.get(
        failure_code,
        "Your payment could not be completed. Please try again.",
    )

    return FailureDiagnosis(
        likely_cause=failure_code,
        severity="medium",
        confidence=0.50,
        explanation=(
            "Deterministic fallback diagnosis used because the LLM "
            "diagnosis service was unavailable."
        ),
        recommended_recovery_focus="use_ml_and_policy_decision",
        customer_message=message,
    )