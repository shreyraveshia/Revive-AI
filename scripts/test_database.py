from datetime import datetime, timezone

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.merchant import Merchant
from app.models.payment_attempt import PaymentAttempt
from app.models.recovery_action import RecoveryAction
from app.models.recovery_outcome import RecoveryOutcome
from app.models.transaction import Transaction


def main() -> None:
    db = SessionLocal()

    try:
        # 1. Create a merchant
        merchant = Merchant(
            name="Urban Threads",
            category="fashion",
        )
        db.add(merchant)
        db.flush()

        # 2. Create a customer
        customer = Customer(
            merchant_id=merchant.id,
            name="Rahul Mehta",
            email="rahul@example.com",
        )
        db.add(customer)
        db.flush()

        # 3. Create a transaction for ₹2,500
        transaction = Transaction(
            merchant_id=merchant.id,
            customer_id=customer.id,
            order_id="TEST-ORDER-001",
            amount=250000,
            currency="INR",
            status="failed",
        )
        db.add(transaction)
        db.flush()

        # 4. Record a failed payment attempt
        payment_attempt = PaymentAttempt(
            transaction_id=transaction.id,
            attempt_number=1,
            payment_method="upi",
            gateway="gateway_a",
            status="failed",
            failure_code="UPI_TIMEOUT",
        )
        db.add(payment_attempt)
        db.flush()

        # 5. Record Revive AI's recovery decision
        recovery_action = RecoveryAction(
            transaction_id=transaction.id,
            action_type="PAYMENT_LINK",
            decision_reason="Initial UPI attempt timed out; payment link is a lower-friction recovery path.",
            confidence=0.91,
            expected_recovery_probability=0.78,
            expected_value_paise=195000,
            status="EXECUTED",
            idempotency_key="test-recovery-001",
            executed_at=datetime.now(timezone.utc),
        )
        db.add(recovery_action)
        db.flush()

        # 6. Record the actual recovery result
        recovery_outcome = RecoveryOutcome(
            recovery_action_id=recovery_action.id,
            status="RECOVERED",
            amount_recovered_paise=250000,
            external_reference="test-payment-link-001",
            notes="Customer completed payment through recovery link.",
            completed_at=datetime.now(timezone.utc),
        )
        db.add(recovery_outcome)

        db.commit()

        print("✅ Test data inserted successfully.")
        print(f"Merchant:          {merchant.id}")
        print(f"Customer:          {customer.id}")
        print(f"Transaction:       {transaction.id}")
        print(f"Payment attempt:   {payment_attempt.id}")
        print(f"Recovery action:   {recovery_action.id}")
        print(f"Recovery outcome:  {recovery_outcome.id}")

        # Read the transaction back from PostgreSQL
        saved_transaction = db.scalar(
            select(Transaction).where(
                Transaction.order_id == "TEST-ORDER-001"
            )
        )

        print("\n✅ Read-back from PostgreSQL:")
        print(f"Order ID:          {saved_transaction.order_id}")
        print(f"Amount (paise):    {saved_transaction.amount}")
        print(f"Status:            {saved_transaction.status}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()