from __future__ import annotations

import pandas as pd


NUMERIC_FEATURES = [
    "amount_paise",
    "customer_previous_transactions",
    "customer_previous_success_rate",
    "customer_previous_avg_amount_paise",
    "merchant_previous_transactions",
    "merchant_previous_success_rate",
    "merchant_previous_avg_amount_paise",
]

CATEGORICAL_FEATURES = [
    "payment_method",
    "failure_code",
    "action",
]

TARGET = "recovered"


def prepare_features(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Select only decision-time features and the target.

    Deliberately excludes transaction_id, recovery_probability,
    and recovered_amount_paise to prevent leakage.
    """

    feature_columns = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    )

    missing = [
        column
        for column in feature_columns + [TARGET]
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    X = df[feature_columns].copy()
    y = df[TARGET].astype(int).copy()

    return X, y