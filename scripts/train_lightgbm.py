from pathlib import Path

import pandas as pd

from app.ml.lightgbm_model import (
    evaluate_lightgbm,
    train_lightgbm,
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

    model, feature_columns = train_lightgbm(train_df)

    validation_metrics = evaluate_lightgbm(
        model,
        feature_columns,
        validation_df,
    )

    test_metrics = evaluate_lightgbm(
        model,
        feature_columns,
        test_df,
    )

    print("=== LIGHTGBM RECOVERY MODEL ===")

    print()
    print("Validation")
    print(f"  ROC-AUC:  {validation_metrics['roc_auc']:.4f}")
    print(f"  PR-AUC:   {validation_metrics['pr_auc']:.4f}")
    print(f"  Log Loss: {validation_metrics['log_loss']:.4f}")

    print()
    print("Test")
    print(f"  ROC-AUC:  {test_metrics['roc_auc']:.4f}")
    print(f"  PR-AUC:   {test_metrics['pr_auc']:.4f}")
    print(f"  Log Loss: {test_metrics['log_loss']:.4f}")


if __name__ == "__main__":
    main()