from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.domain.enums import (
    FailureCode,
    PaymentAttemptStatus,
    PaymentMethod,
    TransactionStatus,
)
from app.simulation.distributions import (
    CustomerProfile,
    MerchantProfile,
    sample_amount_paise,
    sample_customer_profile,
    sample_failure_code_for_method,
    sample_merchant_profile,
    sample_payment_method,
)
from app.simulation.history import EntityHistory, update_history


@dataclass(frozen=True)
class SimulatedCustomer:
    customer_id: str
    profile: CustomerProfile


@dataclass(frozen=True)
class SimulatedMerchant:
    merchant_id: str
    profile: MerchantProfile


@dataclass(frozen=True)
class SimulatedTransaction:
    transaction_id: str
    order_id: str
    merchant_id: str
    customer_id: str
    amount_paise: int
    payment_method: PaymentMethod
    status: TransactionStatus
    failure_code: FailureCode | None
    created_at: datetime

    customer_previous_transactions: int
    customer_previous_success_rate: float
    customer_previous_avg_amount_paise: float

    merchant_previous_transactions: int
    merchant_previous_success_rate: float
    merchant_previous_avg_amount_paise: float


@dataclass
class SyntheticWorld:
    merchants: list[SimulatedMerchant]
    customers: list[SimulatedCustomer]


def create_world(
    merchant_count: int = 100,
    customer_count: int = 5_000,
) -> SyntheticWorld:
    """Create a persistent population of synthetic merchants and customers."""

    merchants = [
        SimulatedMerchant(
            merchant_id=str(uuid4()),
            profile=sample_merchant_profile(),
        )
        for _ in range(merchant_count)
    ]

    customers = [
        SimulatedCustomer(
            customer_id=str(uuid4()),
            profile=sample_customer_profile(),
        )
        for _ in range(customer_count)
    ]

    return SyntheticWorld(
        merchants=merchants,
        customers=customers,
    )


def simulate_payment_attempt(
    customer: CustomerProfile,
    merchant: MerchantProfile,
    payment_method: PaymentMethod,
) -> tuple[PaymentAttemptStatus, FailureCode | None]:
    """
    Simulate the initial payment attempt.

    Success depends on merchant reliability, customer reliability,
    and whether the selected payment method is preferred.
    """

    base_probability = 0.92

    probability = (
        base_probability
        * merchant.reliability
        * (0.75 + 0.25 * customer.reliability)
    )

    if payment_method == customer.preferred_method:
        probability += 0.03

    probability = min(0.99, max(0.05, probability))

    if random.random() < probability:
        return PaymentAttemptStatus.SUCCESS, None

    return (
        PaymentAttemptStatus.FAILED,
        sample_failure_code_for_method(payment_method),
    )


def generate_transaction(
    merchant: SimulatedMerchant,
    customer: SimulatedCustomer,
    created_at: datetime,
) -> SimulatedTransaction:
    """
    Generate one transaction at a specific point in simulated time.
    """

    transaction_id = str(uuid4())
    order_id = f"ORD-{uuid4().hex[:12].upper()}"

    amount_paise = sample_amount_paise()
    payment_method = sample_payment_method()

    status, failure_code = simulate_payment_attempt(
        customer=customer.profile,
        merchant=merchant.profile,
        payment_method=payment_method,
    )

    transaction_status = (
        TransactionStatus.SUCCESS
        if status == PaymentAttemptStatus.SUCCESS
        else TransactionStatus.FAILED
    )

    return SimulatedTransaction(
        transaction_id=transaction_id,
        order_id=order_id,
        merchant_id=merchant.merchant_id,
        customer_id=customer.customer_id,
        amount_paise=amount_paise,
        payment_method=payment_method,
        status=transaction_status,
        failure_code=failure_code,
        created_at=created_at,
        customer_previous_transactions=0,
        customer_previous_success_rate=0.0,
        customer_previous_avg_amount_paise=0.0,
        merchant_previous_transactions=0,
        merchant_previous_success_rate=0.0,
        merchant_previous_avg_amount_paise=0.0,
    )


def generate_transactions(
    world: SyntheticWorld,
    count: int,
    start_time: datetime | None = None,
) -> list[SimulatedTransaction]:
    """
    Generate chronologically ordered transactions while maintaining
    decision-time customer and merchant history.
    """

    if start_time is None:
        start_time = datetime.now(timezone.utc) - timedelta(days=30)

    transactions: list[SimulatedTransaction] = []

    customer_history = {
        customer.customer_id: EntityHistory()
        for customer in world.customers
    }

    merchant_history = {
        merchant.merchant_id: EntityHistory()
        for merchant in world.merchants
    }

    current_time = start_time

    for _ in range(count):
        # Advance simulated time by 1–30 minutes.
        current_time += timedelta(
            minutes=random.randint(1, 30)
        )

        merchant = random.choice(world.merchants)
        customer = random.choice(world.customers)

        customer_stats = customer_history[customer.customer_id]
        merchant_stats = merchant_history[merchant.merchant_id]

        base_transaction = generate_transaction(
            merchant=merchant,
            customer=customer,
            created_at=current_time,
        )

        transaction = SimulatedTransaction(
            **{
                **base_transaction.__dict__,
                "customer_previous_transactions": (
                    customer_stats.transaction_count
                ),
                "customer_previous_success_rate": (
                    customer_stats.success_rate
                ),
                "customer_previous_avg_amount_paise": (
                    customer_stats.average_amount_paise
                ),
                "merchant_previous_transactions": (
                    merchant_stats.transaction_count
                ),
                "merchant_previous_success_rate": (
                    merchant_stats.success_rate
                ),
                "merchant_previous_avg_amount_paise": (
                    merchant_stats.average_amount_paise
                ),
            }
        )

        transactions.append(transaction)

        successful = transaction.status == TransactionStatus.SUCCESS

        # Update history only AFTER decision-time features are captured.
        update_history(
            customer_stats,
            amount_paise=transaction.amount_paise,
            successful=successful,
        )

        update_history(
            merchant_stats,
            amount_paise=transaction.amount_paise,
            successful=successful,
        )

    return transactions