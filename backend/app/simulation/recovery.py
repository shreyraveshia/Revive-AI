from __future__ import annotations

import random

from app.domain.enums import FailureCode, RecoveryActionType
from app.simulation.distributions import (
    CustomerProfile,
    MerchantProfile,
)


def clamp(value: float, minimum: float = 0.01, maximum: float = 0.99) -> float:
    """Keep a probability inside a safe range."""
    return max(minimum, min(maximum, value))


def base_recovery_probability(
    failure_code: FailureCode,
    action: RecoveryActionType,
) -> float:
    """
    Return a baseline probability of recovery for a failure/action pair.

    These are simulation priors, not ML predictions.
    The ML model will later learn from generated outcomes.
    """

    probabilities = {
        FailureCode.UPI_TIMEOUT: {
            RecoveryActionType.NO_ACTION: 0.05,
            RecoveryActionType.RETRY: 0.62,
            RecoveryActionType.ALTERNATE_METHOD: 0.42,
            RecoveryActionType.PAYMENT_LINK: 0.48,
            RecoveryActionType.REMINDER: 0.30,
            RecoveryActionType.ESCALATE: 0.20,
        },
        FailureCode.UPI_DECLINED: {
            RecoveryActionType.NO_ACTION: 0.04,
            RecoveryActionType.RETRY: 0.28,
            RecoveryActionType.ALTERNATE_METHOD: 0.48,
            RecoveryActionType.PAYMENT_LINK: 0.44,
            RecoveryActionType.REMINDER: 0.28,
            RecoveryActionType.ESCALATE: 0.18,
        },
        FailureCode.INSUFFICIENT_FUNDS: {
            RecoveryActionType.NO_ACTION: 0.04,
            RecoveryActionType.RETRY: 0.12,
            RecoveryActionType.ALTERNATE_METHOD: 0.30,
            RecoveryActionType.PAYMENT_LINK: 0.34,
            RecoveryActionType.REMINDER: 0.48,
            RecoveryActionType.ESCALATE: 0.10,
        },
        FailureCode.HARD_DECLINE: {
            RecoveryActionType.NO_ACTION: 0.03,
            RecoveryActionType.RETRY: 0.06,
            RecoveryActionType.ALTERNATE_METHOD: 0.36,
            RecoveryActionType.PAYMENT_LINK: 0.30,
            RecoveryActionType.REMINDER: 0.18,
            RecoveryActionType.ESCALATE: 0.14,
        },
        FailureCode.SOFT_DECLINE: {
            RecoveryActionType.NO_ACTION: 0.04,
            RecoveryActionType.RETRY: 0.36,
            RecoveryActionType.ALTERNATE_METHOD: 0.40,
            RecoveryActionType.PAYMENT_LINK: 0.38,
            RecoveryActionType.REMINDER: 0.25,
            RecoveryActionType.ESCALATE: 0.14,
        },
        FailureCode.NETWORK_ERROR: {
            RecoveryActionType.NO_ACTION: 0.05,
            RecoveryActionType.RETRY: 0.58,
            RecoveryActionType.ALTERNATE_METHOD: 0.38,
            RecoveryActionType.PAYMENT_LINK: 0.40,
            RecoveryActionType.REMINDER: 0.25,
            RecoveryActionType.ESCALATE: 0.16,
        },
        FailureCode.GATEWAY_ERROR: {
            RecoveryActionType.NO_ACTION: 0.04,
            RecoveryActionType.RETRY: 0.52,
            RecoveryActionType.ALTERNATE_METHOD: 0.34,
            RecoveryActionType.PAYMENT_LINK: 0.38,
            RecoveryActionType.REMINDER: 0.22,
            RecoveryActionType.ESCALATE: 0.18,
        },
        FailureCode.AUTHENTICATION_FAILED: {
            RecoveryActionType.NO_ACTION: 0.04,
            RecoveryActionType.RETRY: 0.10,
            RecoveryActionType.ALTERNATE_METHOD: 0.38,
            RecoveryActionType.PAYMENT_LINK: 0.34,
            RecoveryActionType.REMINDER: 0.22,
            RecoveryActionType.ESCALATE: 0.12,
        },
        FailureCode.CHECKOUT_ABANDONED: {
            RecoveryActionType.NO_ACTION: 0.08,
            RecoveryActionType.RETRY: 0.05,
            RecoveryActionType.ALTERNATE_METHOD: 0.20,
            RecoveryActionType.PAYMENT_LINK: 0.58,
            RecoveryActionType.REMINDER: 0.52,
            RecoveryActionType.ESCALATE: 0.08,
        },
    }

    return probabilities[failure_code][action]


def simulate_recovery_probability(
    failure_code: FailureCode,
    action: RecoveryActionType,
    customer: CustomerProfile,
    merchant: MerchantProfile,
    amount_paise: int,
    attempt_number: int = 1,
) -> float:
    """
    Estimate the synthetic probability that a recovery action succeeds.
    """

    probability = base_recovery_probability(
        failure_code=failure_code,
        action=action,
    )

    # Better merchants tend to have healthier checkout/payment operations.
    probability += (merchant.reliability - 0.75) * 0.20

    # Customers with higher recovery affinity respond better to interventions.
    probability += (customer.recovery_affinity - 0.60) * 0.20

    # Reliable customers are somewhat more likely to complete recovery.
    probability += (customer.reliability - 0.75) * 0.10

    # Very expensive transactions introduce additional friction.
    if amount_paise > 500_000:
        probability -= 0.06
    elif amount_paise < 50_000:
        probability += 0.03

    # Repeated attempts suffer from diminishing returns.
    if attempt_number > 1:
        probability -= 0.08 * (attempt_number - 1)

    # Some actions have specific contextual effects.
    if (
        action == RecoveryActionType.RETRY
        and failure_code
        in {
            FailureCode.UPI_TIMEOUT,
            FailureCode.NETWORK_ERROR,
            FailureCode.GATEWAY_ERROR,
        }
    ):
        probability += 0.05

    if (
        action == RecoveryActionType.RETRY
        and failure_code
        in {
            FailureCode.INSUFFICIENT_FUNDS,
            FailureCode.HARD_DECLINE,
            FailureCode.AUTHENTICATION_FAILED,
        }
    ):
        probability -= 0.06

    if (
        action == RecoveryActionType.PAYMENT_LINK
        and failure_code == FailureCode.CHECKOUT_ABANDONED
    ):
        probability += 0.08

    if (
        action == RecoveryActionType.REMINDER
        and failure_code == FailureCode.INSUFFICIENT_FUNDS
    ):
        probability += 0.07

    return clamp(probability)


def simulate_recovery_outcome(
    failure_code: FailureCode,
    action: RecoveryActionType,
    customer: CustomerProfile,
    merchant: MerchantProfile,
    amount_paise: int,
    attempt_number: int = 1,
) -> tuple[bool, float]:
    """
    Simulate one binary recovery outcome.

    Returns:
        (recovered, probability_used)
    """

    probability = simulate_recovery_probability(
        failure_code=failure_code,
        action=action,
        customer=customer,
        merchant=merchant,
        amount_paise=amount_paise,
        attempt_number=attempt_number,
    )

    recovered = random.random() < probability

    return recovered, probability