from __future__ import annotations

import random
from dataclasses import dataclass

from app.domain.enums import FailureCode, PaymentMethod


@dataclass(frozen=True)
class CustomerProfile:
    reliability: float
    preferred_method: PaymentMethod
    recovery_affinity: float


@dataclass(frozen=True)
class MerchantProfile:
    reliability: float
    category: str


PAYMENT_METHOD_WEIGHTS = {
    PaymentMethod.UPI: 0.55,
    PaymentMethod.CARD: 0.25,
    PaymentMethod.NETBANKING: 0.12,
    PaymentMethod.WALLET: 0.08,
}


FAILURE_WEIGHTS = {
    FailureCode.UPI_TIMEOUT: 0.15,
    FailureCode.UPI_DECLINED: 0.10,
    FailureCode.INSUFFICIENT_FUNDS: 0.18,
    FailureCode.HARD_DECLINE: 0.10,
    FailureCode.SOFT_DECLINE: 0.12,
    FailureCode.NETWORK_ERROR: 0.10,
    FailureCode.GATEWAY_ERROR: 0.08,
    FailureCode.AUTHENTICATION_FAILED: 0.07,
    FailureCode.CHECKOUT_ABANDONED: 0.10,
}

PAYMENT_METHOD_FAILURE_WEIGHTS = {
    PaymentMethod.UPI: {
        FailureCode.UPI_TIMEOUT: 0.22,
        FailureCode.UPI_DECLINED: 0.15,
        FailureCode.NETWORK_ERROR: 0.18,
        FailureCode.GATEWAY_ERROR: 0.12,
        FailureCode.INSUFFICIENT_FUNDS: 0.13,
        FailureCode.SOFT_DECLINE: 0.10,
        FailureCode.CHECKOUT_ABANDONED: 0.10,
    },
    PaymentMethod.CARD: {
        FailureCode.INSUFFICIENT_FUNDS: 0.20,
        FailureCode.HARD_DECLINE: 0.16,
        FailureCode.SOFT_DECLINE: 0.18,
        FailureCode.AUTHENTICATION_FAILED: 0.15,
        FailureCode.NETWORK_ERROR: 0.12,
        FailureCode.GATEWAY_ERROR: 0.10,
        FailureCode.CHECKOUT_ABANDONED: 0.09,
    },
    PaymentMethod.NETBANKING: {
        FailureCode.AUTHENTICATION_FAILED: 0.20,
        FailureCode.NETWORK_ERROR: 0.20,
        FailureCode.GATEWAY_ERROR: 0.15,
        FailureCode.SOFT_DECLINE: 0.15,
        FailureCode.INSUFFICIENT_FUNDS: 0.12,
        FailureCode.CHECKOUT_ABANDONED: 0.18,
    },
    PaymentMethod.WALLET: {
        FailureCode.INSUFFICIENT_FUNDS: 0.20,
        FailureCode.AUTHENTICATION_FAILED: 0.15,
        FailureCode.NETWORK_ERROR: 0.20,
        FailureCode.GATEWAY_ERROR: 0.15,
        FailureCode.SOFT_DECLINE: 0.10,
        FailureCode.CHECKOUT_ABANDONED: 0.20,
    },
}

def sample_failure_code_for_method(
    payment_method: PaymentMethod,
) -> FailureCode:
    return weighted_choice(
        PAYMENT_METHOD_FAILURE_WEIGHTS[payment_method]
    )



MERCHANT_CATEGORIES = [
    "fashion",
    "electronics",
    "food",
    "beauty",
    "travel",
    "education",
    "health",
    "home",
]


def weighted_choice[T](weights: dict[T, float]) -> T:
    items = list(weights.keys())
    probabilities = list(weights.values())

    return random.choices(
        items,
        weights=probabilities,
        k=1,
    )[0]


def sample_payment_method() -> PaymentMethod:
    return weighted_choice(PAYMENT_METHOD_WEIGHTS)


def sample_failure_code() -> FailureCode:
    return weighted_choice(FAILURE_WEIGHTS)


def sample_amount_paise() -> int:
    """
    Generate a right-skewed transaction amount.

    Most transactions are relatively small, while a smaller
    number are substantially larger.
    """

    rupees = random.lognormvariate(
        mu=7.2,
        sigma=0.9,
    )

    rupees = max(100, min(100_000, rupees))

    return int(round(rupees * 100))


def sample_customer_profile() -> CustomerProfile:
    return CustomerProfile(
        reliability=random.betavariate(8, 2),
        preferred_method=sample_payment_method(),
        recovery_affinity=random.betavariate(5, 3),
    )


def sample_merchant_profile() -> MerchantProfile:
    return MerchantProfile(
        reliability=random.betavariate(9, 1.5),
        category=random.choice(MERCHANT_CATEGORIES),
    )