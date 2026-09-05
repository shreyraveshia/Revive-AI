from __future__ import annotations

import pandas as pd
import lightgbm as lgb

from app.ml.lightgbm_model import prepare_lightgbm_features
from app.policy.engine import apply_policy


def evaluate_policy(
    model: lgb.LGBMClassifier,
    feature_columns: list[str],
    test_df: pd.DataFrame,
) -> dict[str, object]:
    """
    Evaluate LightGBM predictions after deterministic policy enforcement.
    """

    prediction_df = test_df.copy()

    X, _ = prepare_lightgbm_features(prediction_df)

    X = X.reindex(
        columns=feature_columns,
        fill_value=0,
    )

    prediction_df["predicted_probability"] = (
        model.predict_proba(X)[:, 1]
    )

    transaction_rows = (
        prediction_df[
            [
                "transaction_id",
                "amount_paise",
                "failure_code",
            ]
        ]
        .drop_duplicates("transaction_id")
    )

    selected_rows: list[pd.Series] = []

    blocked_action_counts: dict[str, int] = {}

    reason_counts: dict[str, int] = {}

    for _, transaction in transaction_rows.iterrows():
        transaction_id = transaction["transaction_id"]

        group = prediction_df[
            prediction_df["transaction_id"] == transaction_id
        ].copy()

        probabilities = {
            row["action"]: float(row["predicted_probability"])
            for _, row in group.iterrows()
        }

        policy_result = apply_policy(
            action_probabilities=probabilities,
            amount_paise=int(transaction["amount_paise"]),
            attempt_number=1,
            failure_code=str(transaction["failure_code"]),
        )

        reason_counts[policy_result.reason] = (
            reason_counts.get(policy_result.reason, 0) + 1
        )

        selected = group[
            group["action"] == policy_result.selected_action
        ]

        if len(selected) != 1:
            raise ValueError(
                f"Expected exactly one selected row for "
                f"{transaction_id}, got {len(selected)}."
            )

        selected_rows.append(selected.iloc[0])

    selected_df = pd.DataFrame(selected_rows)

    revenue_at_risk = int(
        transaction_rows["amount_paise"].sum()
    )

    recovered_revenue = int(
        selected_df["recovered_amount_paise"].sum()
    )

    recovery_rate = (
        recovered_revenue / revenue_at_risk
        if revenue_at_risk
        else 0.0
    )

    action_counts = (
        selected_df["action"]
        .value_counts()
        .to_dict()
    )

    return {
        "transactions": len(transaction_rows),
        "revenue_at_risk_paise": revenue_at_risk,
        "recovered_revenue_paise": recovered_revenue,
        "recovery_rate": recovery_rate,
        "action_counts": action_counts,
        "reason_counts": reason_counts,
    }