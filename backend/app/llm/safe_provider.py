from __future__ import annotations

from app.llm.groq_provider import GroqProvider
from app.llm.provider import LLMProvider
from app.llm.schemas import (
    FailureDiagnosis,
    build_fallback_diagnosis,
)


class SafeLLMProvider(LLMProvider):
    """
    LLM provider with deterministic fallback behavior.

    LLM failure must never prevent the revenue-recovery
    decision engine from operating.
    """

    def __init__(self) -> None:
        self.provider: LLMProvider | None = None
        self.initialization_error: str | None = None

        try:
            self.provider = GroqProvider()
        except Exception as exc:
            self.initialization_error = str(exc)

    def diagnose_failure(
        self,
        *,
        transaction_amount_paise: int,
        payment_method: str,
        failure_code: str,
        attempt_number: int,
        customer_previous_transactions: int,
        customer_previous_success_rate: float,
        merchant_previous_success_rate: float,
    ) -> FailureDiagnosis:
        if self.provider is None:
            return build_fallback_diagnosis(
                failure_code=failure_code,
            )

        try:
            return self.provider.diagnose_failure(
                transaction_amount_paise=transaction_amount_paise,
                payment_method=payment_method,
                failure_code=failure_code,
                attempt_number=attempt_number,
                customer_previous_transactions=(
                    customer_previous_transactions
                ),
                customer_previous_success_rate=(
                    customer_previous_success_rate
                ),
                merchant_previous_success_rate=(
                    merchant_previous_success_rate
                ),
            )
        except Exception:
            return build_fallback_diagnosis(
                failure_code=failure_code,
            )