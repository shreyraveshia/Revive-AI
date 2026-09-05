from __future__ import annotations

from abc import ABC, abstractmethod

from app.llm.schemas import FailureDiagnosis


class LLMProvider(ABC):
    """Interface implemented by LLM providers."""

    @abstractmethod
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
        """Diagnose a failed payment."""
        raise NotImplementedError