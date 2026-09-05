from pathlib import Path

import pandas as pd

from app.evaluation.baselines import BaselineResult


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = PROJECT_ROOT / "data" / "processed" / "test.csv"


def choose_rule_based_action(row: pd.Series) -> str:
    failure_code = row["failure_code"]

    if failure_code in {
        "upi_timeout",
        "network_error",
        "gateway_error",
        "soft_decline",
    }:
        return "retry"

    if failure_code == "insufficient_funds":
        return "reminder"

    if failure_code == "checkout_abandoned":
        return "payment_link"

    if failure_code in {
        "hard_decline",
        "authentication_failed",
        "upi_declined",
    }:
        return "alternate_method"

    return "no_action"


def main() -> None:
    test_df = pd.read_csv(
        TEST_PATH,
        parse_dates=["created_at"],
    )

    # Keep one row per transaction for the decision.
    transaction_df = (
        test_df.sort_values("created_at")
        .drop_duplicates("transaction_id")
        .copy()
    )

    transaction_df["chosen_action"] = transaction_df.apply(
        choose_rule_based_action,
        axis=1,
    )

    selected_rows = []

    for _, transaction in transaction_df.iterrows():
        matches = test_df[
            (test_df["transaction_id"] == transaction["transaction_id"])
            & (test_df["action"] == transaction["chosen_action"])
        ]

        if len(matches) != 1:
            raise ValueError(
                f"Expected exactly one matching outcome for "
                f"{transaction['transaction_id']}, "
                f"got {len(matches)}."
            )

        selected_rows.append(matches.iloc[0])

    selected_df = pd.DataFrame(selected_rows)

    revenue_at_risk = int(
        transaction_df["amount_paise"].sum()
    )

    recovered_revenue = int(
        selected_df["recovered_amount_paise"].sum()
    )

    result = BaselineResult(
        name="SIMPLE_RULES",
        transactions_evaluated=len(transaction_df),
        revenue_at_risk_paise=revenue_at_risk,
        recovered_revenue_paise=recovered_revenue,
    )

    print("=== SIMPLE RULES BASELINE ===")
    print(
        f"Transactions evaluated: "
        f"{result.transactions_evaluated:,}"
    )
    print(
        f"Revenue at risk: "
        f"₹{result.revenue_at_risk_rupees:,.2f}"
    )
    print(
        f"Recovered revenue: "
        f"₹{result.recovered_revenue_rupees:,.2f}"
    )
    print(
        f"Recovery rate: "
        f"{result.recovery_rate:.2%}"
    )

    print()
    print("Chosen actions:")
    print(transaction_df["chosen_action"].value_counts())


if __name__ == "__main__":
    main()