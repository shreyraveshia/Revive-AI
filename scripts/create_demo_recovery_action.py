from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.merchant import Merchant
from app.models.payment_attempt import PaymentAttempt
from app.models.recovery_action import RecoveryAction
from app.models.transaction import Transaction


def main() -> None:
    db = SessionLocal()

    try:
        merchant = Merchant(
            name="Revive Demo Store",
            category="fashion",
        )
        db.add(merchant)
        db.flush()

        customer = Customer(
            merchant_id=merchant.id,
            name="Revive Demo Customer",
            email="revive-demo@example.com",
        )
        db.add(customer)
        db.flush()

        transaction = Transaction(
            merchant_id=merchant.id,
            customer_id=customer.id,
            order_id="REVIVE-DEMO-ORDER-001",
            amount=10000,
            currency="INR",
            status="failed",
        )
        db.add(transaction)
        db.flush()

        payment_attempt = PaymentAttempt(
            transaction_id=transaction.id,
            attempt_number=1,
            payment_method="upi",
            gateway="demo_gateway",
            status="failed",
            failure_code="upi_timeout",
        )
        db.add(payment_attempt)
        db.flush()

        action = RecoveryAction(
            transaction_id=transaction.id,
            action_type="payment_link",
            decision_reason="Demo execution of a bounded Payment Link recovery.",
            confidence=0.90,
            expected_recovery_probability=0.55,
            expected_value_paise=5000,
            status="PROPOSED",
            idempotency_key="REVIVE-DEMO-ACTION-001",
        )
        db.add(action)

        db.commit()

        print("✅ Demo recovery action created.")
        print(f"Merchant:          {merchant.id}")
        print(f"Customer:          {customer.id}")
        print(f"Transaction:       {transaction.id}")
        print(f"Payment attempt:   {payment_attempt.id}")
        print(f"Recovery action:   {action.id}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()