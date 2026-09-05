from pathlib import Path

import pandas as pd
import lightgbm as lgb

from app.decision.engine import choose_best_action
from app.ml.lightgbm_model import prepare_lightgbm_features


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

    model, feature_columns = _train_model(train_df)

    X, _ = prepare_lightgbm_features(test_df)

    X = X.reindex(
        columns=feature_columns,
        fill_value=0,
    )

    test_df = test_df.copy()

    test_df["predicted_probability"] = (
        model.predict_proba(X)[:, 1]
    )

    decisions = []

    for transaction_id, group in test_df.groupby(
        "transaction_id",
        sort=False,
    ):
        amount = int(group["amount_paise"].iloc[0])

        predicted = {
            row["action"]: row["predicted_probability"]
            for _, row in group.iterrows()
        }

        decision = choose_best_action(
            action_probabilities=predicted,
            amount_paise=amount,
        )

        true_best = group.loc[
            group["recovery_probability"].idxmax()
        ]["action"]

        decisions.append(
            {
                "transaction_id": transaction_id,
                "selected_action": decision.selected_action,
                "true_best_action": true_best,
            }
        )

    decisions_df = pd.DataFrame(decisions)

    agreement = (
        decisions_df["selected_action"]
        == decisions_df["true_best_action"]
    ).mean()

    print("=== PROBABILITY-RANKING DIAGNOSTIC ===")
    print(
        f"Transactions: {len(decisions_df):,}"
    )
    print(
        f"Agreement with true probability-best action: "
        f"{agreement:.2%}"
    )

    print()
    print("Selected action distribution:")

    print(
        decisions_df["selected_action"]
        .value_counts()
    )


def _train_model(
    train_df: pd.DataFrame,
) -> tuple[lgb.LGBMClassifier, list[str]]:
    from app.ml.lightgbm_model import train_lightgbm

    return train_lightgbm(train_df)


if __name__ == "__main__":
    main()