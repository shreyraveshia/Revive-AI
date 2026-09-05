from pathlib import Path

import pandas as pd

from app.evaluation.decision_diagnostics import diagnose_decisions
from app.ml.lightgbm_model import train_lightgbm


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRAIN_PATH = PROJECT_ROOT / "data" / "processed" / "train.csv"
TEST_PATH = PROJECT_ROOT / "data" / "processed" / "test.csv"


def main() -> None:
    train_df = pd.read_csv(
        TRAIN_PATH,
        parse_dates=["created_at"],
    )

    test_df = pd.read_csv(
        TEST_PATH,
        parse_dates=["created_at"],
    )

    model, feature_columns = train_lightgbm(
        train_df
    )

    result = diagnose_decisions(
        model=model,
        feature_columns=feature_columns,
        test_df=test_df,
    )

    print("=== REVIVE AI DECISION DIAGNOSTICS ===")

    print(
        f"Transactions: "
        f"{result['transactions']:,}"
    )

    print(
        f"Model/oracle action agreement: "
        f"{result['agreement_rate']:.2%}"
    )

    print(
        f"Revive recovered revenue: "
        f"₹{result['revive_revenue_paise'] / 100:,.2f}"
    )

    print(
        f"Oracle recovered revenue: "
        f"₹{result['oracle_revenue_paise'] / 100:,.2f}"
    )

    print(
        f"Oracle gap: "
        f"₹{result['oracle_gap_paise'] / 100:,.2f}"
    )

    print()
    print("Revive selected actions:")

    for action, count in result["action_counts"].items():
        print(
            f"  {action}: {count:,}"
        )


if __name__ == "__main__":
    main()