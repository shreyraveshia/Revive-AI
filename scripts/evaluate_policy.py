from pathlib import Path

import pandas as pd

from app.ml.lightgbm_model import train_lightgbm
from app.evaluation.policy_evaluation import evaluate_policy


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRAIN_PATH = (
    PROJECT_ROOT / "data" / "processed" / "train.csv"
)

TEST_PATH = (
    PROJECT_ROOT / "data" / "processed" / "test.csv"
)


def main() -> None:
    train_df = pd.read_csv(
        TRAIN_PATH,
        parse_dates=["created_at"],
    )

    test_df = pd.read_csv(
        TEST_PATH,
        parse_dates=["created_at"],
    )

    print("Training LightGBM...")
    model, feature_columns = train_lightgbm(train_df)

    print("Evaluating policy-aware Revive AI...")

    result = evaluate_policy(
        model=model,
        feature_columns=feature_columns,
        test_df=test_df,
    )

    print()
    print("=== REVIVE AI POLICY EVALUATION ===")

    print(
        f"Transactions evaluated: "
        f"{result['transactions']:,}"
    )

    print(
        f"Revenue at risk: "
        f"₹{result['revenue_at_risk_paise'] / 100:,.2f}"
    )

    print(
        f"Recovered revenue: "
        f"₹{result['recovered_revenue_paise'] / 100:,.2f}"
    )

    print(
        f"Recovery rate: "
        f"{result['recovery_rate']:.2%}"
    )

    print()
    print("Selected actions:")

    for action, count in result["action_counts"].items():
        print(f"  {action}: {count:,}")

    print()
    print("Policy outcomes:")

    for reason, count in result["reason_counts"].items():
        print(f"  {reason}: {count:,}")


if __name__ == "__main__":
    main()