from pathlib import Path

import pandas as pd

from app.evaluation.baselines import evaluate_baselines


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = PROJECT_ROOT / "data" / "processed" / "test.csv"


def main() -> None:
    print(f"Loading test dataset: {TEST_PATH}")

    test_df = pd.read_csv(
        TEST_PATH,
        parse_dates=["created_at"],
    )

    results = evaluate_baselines(test_df)

    print()
    print("=== REVIVE AI BASELINE EVALUATION ===")

    for result in results:
        print()
        print(result.name)
        print(f"  Transactions evaluated: {result.transactions_evaluated:,}")
        print(
            f"  Revenue at risk: "
            f"₹{result.revenue_at_risk_rupees:,.2f}"
        )
        print(
            f"  Recovered revenue: "
            f"₹{result.recovered_revenue_rupees:,.2f}"
        )
        print(
            f"  Recovery rate: "
            f"{result.recovery_rate:.2%}"
        )


if __name__ == "__main__":
    main()