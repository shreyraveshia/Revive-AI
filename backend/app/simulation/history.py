from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EntityHistory:
    transaction_count: int = 0
    successful_transactions: int = 0
    total_amount_paise: int = 0

    @property
    def success_rate(self) -> float:
        if self.transaction_count == 0:
            return 0.0

        return self.successful_transactions / self.transaction_count

    @property
    def average_amount_paise(self) -> float:
        if self.transaction_count == 0:
            return 0.0

        return self.total_amount_paise / self.transaction_count


def update_history(
    history: EntityHistory,
    *,
    amount_paise: int,
    successful: bool,
) -> None:
    """
    Update history AFTER a transaction outcome is known.

    This ordering is important for avoiding target leakage.
    """

    history.transaction_count += 1
    history.total_amount_paise += amount_paise

    if successful:
        history.successful_transactions += 1