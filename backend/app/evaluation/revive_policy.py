from __future__ import annotations

import pandas as pd
import lightgbm as lgb

from app.decision.engine import choose_best_action
from app.ml.lightgbm_model import prepare_lightgbm_features


def evaluate_revive_policy(
    model: lgb.LGBMClassifier,
    feature_columns: list[str],
    test_df: pd.DataFrame,
) -> dict[str, float]:
    """
    Evaluate the ML + expected-value decision policy.

    One action is selected per failed transaction.
    The selected action's actual simulated outcome is then used
    to measure recovered revenue.
    """

    # Get one transaction-level row for each failed transaction.
    transaction_df = (
        test_df[
            [
                "transaction_id",
                "created_at",
                "amount_paise",
                "payment_method",
                "failure_code",
                "customer_previous_transactions",
                "customer_previous_success_rate",
                "customer_previous_avg_amount_paise",
                "merchant_previous_transactions",
                "merchant_previous_success_rate",
                "merchant_previous_avg_amount_paise",
            ]
        ]
        .drop_duplicates("transaction_id")
        .copy()
    )

    # Every failed transaction should have exactly six candidate rows
    # in the original action-level test dataset.
    action_predictions = test_df.copy()

    X_test, _ = prepare_lightgbm_features(
        action_predictions
    )

    X_test = X_test.reindex(
        columns=feature_columns,
        fill_value=0,
    )

    action_predictions["predicted_probability"] = (
        model.predict_proba(X_test)[:, 1]
    )

    selected_rows = []

    for transaction_id, group in action_predictions.groupby(
        "transaction_id",
        sort=False,
    ):
        transaction = transaction_df[
            transaction_df["transaction_id"] == transaction_id
        ].iloc[0]

        probabilities = {
            row["action"]: row["predicted_probability"]
            for _, row in group.iterrows()
        }

        decision = choose_best_action(
            action_probabilities=probabilities,
            amount_paise=int(transaction["amount_paise"]),
        )

        selected = group[
            group["action"] == decision.selected_action
        ]

        if len(selected) != 1:
            raise ValueError(
                f"Expected exactly one selected action for "
                f"transaction {transaction_id}, "
                f"got {len(selected)}."
            )

        selected_rows.append(selected.iloc[0])

    selected_df = pd.DataFrame(selected_rows)

    revenue_at_risk = int(
        transaction_df["amount_paise"].sum()
    )

    recovered_revenue = int(
        selected_df["recovered_amount_paise"].sum()
    )

    recovery_rate = (
        recovered_revenue / revenue_at_risk
        if revenue_at_risk
        else 0.0
    )

    return {
        "transactions_evaluated": len(transaction_df),
        "revenue_at_risk_paise": revenue_at_risk,
        "recovered_revenue_paise": recovered_revenue,
        "recovery_rate": recovery_rate,
    }