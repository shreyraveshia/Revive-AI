from pathlib import Path

import pandas as pd

from app.agent.context import RecoveryContext
from app.agent.service import ReviveAgent
from app.ml.lightgbm_model import train_lightgbm


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRAIN_PATH = (
    PROJECT_ROOT / "data" / "processed" / "train.csv"
)


def main() -> None:
    train_df = pd.read_csv(
        TRAIN_PATH,
        parse_dates=["created_at"],
    )

    model, feature_columns = train_lightgbm(
        train_df
    )

    agent = ReviveAgent(
        recovery_model=model,
        feature_columns=feature_columns,
    )

    context = RecoveryContext(
        transaction_id="demo-transaction-001",
        amount_paise=250000,
        payment_method="upi",
        failure_code="upi_timeout",
        attempt_number=1,
        customer_previous_transactions=3,
        customer_previous_success_rate=0.67,
        customer_previous_avg_amount_paise=180000,
        merchant_previous_transactions=250,
        merchant_previous_success_rate=0.91,
        merchant_previous_avg_amount_paise=210000,
    )

    result = agent.decide(context)

    print("=== REVIVE AI AGENT ===")

    print()
    print("Diagnosis:")
    print(
        result.diagnosis.model_dump_json(
            indent=2
        )
    )

    print()
    print("Selected action:")
    print(
        result.policy_result.selected_action
    )

    print()
    print("Decision reason:")
    print(
        result.policy_result.reason
    )

    print()
    print("Action scores:")

    for score in result.policy_result.scores:
        print(
            f"  {score.action:20}"
            f" probability={score.recovery_probability:.3f}"
            f" EV={score.expected_value_paise:.0f}"
        )


if __name__ == "__main__":
    main()