from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime

from app.domain.enums import RecoveryActionType
from app.simulation.counterfactual import simulate_all_actions
from app.simulation.generator import SimulatedTransaction, SyntheticWorld


@dataclass(frozen=True)
class RecoveryDatasetRow:
    transaction_id: str
    created_at: datetime
    amount_paise: int
    payment_method: str
    failure_code: str

    customer_previous_transactions: int
    customer_previous_success_rate: float
    customer_previous_avg_amount_paise: float

    merchant_previous_transactions: int
    merchant_previous_success_rate: float
    merchant_previous_avg_amount_paise: float

    action: str
    recovery_probability: float
    recovered: int
    recovered_amount_paise: int


def build_recovery_dataset(
    world: SyntheticWorld,
    transactions: list[SimulatedTransaction],
) -> list[RecoveryDatasetRow]:
    """
    Expand failed transactions into one row per candidate recovery action.
    """

    rows: list[RecoveryDatasetRow] = []

    customer_profiles = {
        customer.customer_id: customer.profile
        for customer in world.customers
    }

    merchant_profiles = {
        merchant.merchant_id: merchant.profile
        for merchant in world.merchants
    }

    for transaction in transactions:
        if transaction.failure_code is None:
            continue

        customer = customer_profiles[transaction.customer_id]
        merchant = merchant_profiles[transaction.merchant_id]

        outcomes = simulate_all_actions(
            failure_code=transaction.failure_code,
            customer=customer,
            merchant=merchant,
            amount_paise=transaction.amount_paise,
            attempt_number=1,
        )

        for outcome in outcomes:
            rows.append(
                RecoveryDatasetRow(
                    transaction_id=transaction.transaction_id,
                    created_at=transaction.created_at,
                    amount_paise=transaction.amount_paise,
                    payment_method=transaction.payment_method.value,
                    failure_code=transaction.failure_code.value,
                    customer_previous_transactions=(
                        transaction.customer_previous_transactions
                    ),
                    customer_previous_success_rate=(
                        transaction.customer_previous_success_rate
                    ),
                    customer_previous_avg_amount_paise=(
                        transaction.customer_previous_avg_amount_paise
                    ),
                    merchant_previous_transactions=(
                        transaction.merchant_previous_transactions
                    ),
                    merchant_previous_success_rate=(
                        transaction.merchant_previous_success_rate
                    ),
                    merchant_previous_avg_amount_paise=(
                        transaction.merchant_previous_avg_amount_paise
                    ),
                    action=outcome.action.value,
                    recovery_probability=outcome.recovery_probability,
                    recovered=int(outcome.recovered),
                    recovered_amount_paise=outcome.recovered_amount_paise,
                )
            )

    return rows