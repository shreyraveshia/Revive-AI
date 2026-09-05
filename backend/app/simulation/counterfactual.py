from __future__ import annotations

from dataclasses import dataclass

from app.domain.enums import FailureCode, RecoveryActionType
from app.simulation.distributions import (
    CustomerProfile,
    MerchantProfile,
)
from app.simulation.recovery import simulate_recovery_outcome


@dataclass(frozen=True)
class CounterfactualOutcome:
    action: RecoveryActionType
    recovery_probability: float
    recovered: bool
    recovered_amount_paise: int


def simulate_all_actions(
    failure_code: FailureCode,
    customer: CustomerProfile,
    merchant: MerchantProfile,
    amount_paise: int,
    attempt_number: int = 1,
) -> list[CounterfactualOutcome]:
    """
    Simulate one potential outcome for every recovery action.
    """

    outcomes: list[CounterfactualOutcome] = []

    for action in RecoveryActionType:
        recovered, probability = simulate_recovery_outcome(
            failure_code=failure_code,
            action=action,
            customer=customer,
            merchant=merchant,
            amount_paise=amount_paise,
            attempt_number=attempt_number,
        )

        outcomes.append(
            CounterfactualOutcome(
                action=action,
                recovery_probability=probability,
                recovered=recovered,
                recovered_amount_paise=amount_paise if recovered else 0,
            )
        )

    return outcomes