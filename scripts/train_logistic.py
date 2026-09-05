from pathlib import Path

import pandas as pd

from app.ml.recovery_model import (
    build_logistic_regression,
    evaluate_model,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRAIN_PATH = PROJECT_ROOT / "data" / "processed" / "train.csv"
VALIDATION_PATH = (
    PROJECT_ROOT / "data" / "processed" / "validation.csv"
)
TEST_PATH = PROJECT_ROOT / "data" / "processed" / "test.csv"


def main() -> None:
    train_df = pd.read_csv(
        TRAIN_PATH,
        parse_dates=["created_at"],
    )

    validation_df = pd.read_csv(
        VALIDATION_PATH,
        parse_dates=["created_at"],
    )

    test_df = pd.read_csv(
        TEST_PATH,
        parse_dates=["created_at"],
    )

    model = build_logistic_regression()

    X_train = train_df[
        [
            "amount_paise",
            "payment_method",
            "failure_code",
            "customer_previous_transactions",
            "customer_previous_success_rate",
            "customer_previous_avg_amount_paise",
            "merchant_previous_transactions",
            "merchant_previous_success_rate",
            "merchant_previous_avg_amount_paise",
            "action",
        ]
    ]

    y_train = train_df["recovered"].astype(int)

    model.fit(X_train, y_train)

    validation_metrics = evaluate_model(
        model,
        validation_df,
    )

    test_metrics = evaluate_model(
        model,
        test_df,
    )

    print("=== LOGISTIC REGRESSION ===")

    print()
    print("Validation")
    print(f"  ROC-AUC:  {validation_metrics.roc_auc:.4f}")
    print(f"  PR-AUC:   {validation_metrics.pr_auc:.4f}")
    print(f"  Log Loss: {validation_metrics.log_loss:.4f}")

    print()
    print("Test")
    print(f"  ROC-AUC:  {test_metrics.roc_auc:.4f}")
    print(f"  PR-AUC:   {test_metrics.pr_auc:.4f}")
    print(f"  Log Loss: {test_metrics.log_loss:.4f}")


if __name__ == "__main__":
    main()