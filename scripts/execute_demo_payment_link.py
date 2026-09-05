from __future__ import annotations

from app.executor.service import execute_payment_link_for_action


RECOVERY_ACTION_ID = "9449f98b-c366-4550-be02-eb4fcb9489cb"


def main() -> None:
    result = execute_payment_link_for_action(
        recovery_action_id=RECOVERY_ACTION_ID,
        amount_paise=10000,
        reference_id="REVIVE-DEMO-PL02",
        description="Revive AI Test Recovery",
        customer_name="Revive Demo Customer",
        customer_email="revive-demo@example.com",
    )

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()