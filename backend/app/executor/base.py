from __future__ import annotations

from abc import ABC, abstractmethod

from app.executor.schemas import ExecutionResult


class RecoveryExecutor(ABC):
    """Interface for bounded recovery action execution."""

    @abstractmethod
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
        raise NotImplementedError