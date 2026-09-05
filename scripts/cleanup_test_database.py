from sqlalchemy import delete

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
        db.execute(
            delete(RecoveryOutcome).where(
                RecoveryOutcome.external_reference == "test-payment-link-001"
            )
        )

        db.execute(
            delete(RecoveryAction).where(
                RecoveryAction.idempotency_key == "test-recovery-001"
            )
        )

        db.execute(
            delete(PaymentAttempt).where(
                PaymentAttempt.transaction_id.in_(
                    db.query(Transaction.id)
                    .filter(Transaction.order_id == "TEST-ORDER-001")
                )
            )
        )

        db.execute(
            delete(Transaction).where(
                Transaction.order_id == "TEST-ORDER-001"
            )
        )

        db.execute(
            delete(Customer).where(
                Customer.email == "rahul@example.com"
            )
        )

        db.execute(
            delete(Merchant).where(
                Merchant.name == "Urban Threads"
            )
        )

        db.commit()
        print("✅ Test data cleaned up.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()