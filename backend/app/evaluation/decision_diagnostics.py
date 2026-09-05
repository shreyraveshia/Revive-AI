from __future__ import annotations

import pandas as pd
import lightgbm as lgb

from app.decision.engine import choose_best_action
from app.ml.lightgbm_model import prepare_lightgbm_features


def diagnose_decisions(
    model: lgb.LGBMClassifier,
    feature_columns: list[str],
    test_df: pd.DataFrame,
) -> dict[str, object]:
    action_df = test_df.copy()

    X, _ = prepare_lightgbm_features(action_df)

    X = X.reindex(
        columns=feature_columns,
        fill_value=0,
    )

    action_df["predicted_probability"] = (
        model.predict_proba(X)[:, 1]
    )

    decisions = []

    for transaction_id, group in action_df.groupby(
        "transaction_id",
        sort=False,
    ):
        amount = int(group["amount_paise"].iloc[0])

        predicted_probabilities = {
            row["action"]: row["predicted_probability"]
            for _, row in group.iterrows()
        }

        decision = choose_best_action(
            action_probabilities=predicted_probabilities,
            amount_paise=amount,
        )

        # Actual best action under the simulator.
        oracle_row = group.loc[
            group["recovered_amount_paise"].idxmax()
        ]

        decisions.append(
            {
                "transaction_id": transaction_id,
                "selected_action": decision.selected_action,
                "selected_recovery": int(
                    group.loc[
                        group["action"] == decision.selected_action,
                        "recovered_amount_paise",
                    ].iloc[0]
                ),
                "oracle_action": oracle_row["action"],
                "oracle_recovery": int(
                    oracle_row["recovered_amount_paise"]
                ),
            }
        )

    decisions_df = pd.DataFrame(decisions)

    agreement = (
        decisions_df["selected_action"]
        == decisions_df["oracle_action"]
    ).mean()

    revive_revenue = int(
        decisions_df["selected_recovery"].sum()
    )

    oracle_revenue = int(
        decisions_df["oracle_recovery"].sum()
    )

    action_counts = (
        decisions_df["selected_action"]
        .value_counts()
        .to_dict()
    )

    return {
        "transactions": len(decisions_df),
        "agreement_rate": agreement,
        "revive_revenue_paise": revive_revenue,
        "oracle_revenue_paise": oracle_revenue,
        "oracle_gap_paise": oracle_revenue - revive_revenue,
        "action_counts": action_counts,
    }