from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RecoveryContext:
    transaction_id: str
    amount_paise: int
    payment_method: str
    failure_code: str
    attempt_number: int

    customer_previous_transactions: int
    customer_previous_success_rate: float
    customer_previous_avg_amount_paise: float

    merchant_previous_transactions: int
    merchant_previous_success_rate: float
    merchant_previous_avg_amount_paise: float