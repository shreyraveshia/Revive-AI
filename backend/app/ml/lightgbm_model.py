from __future__ import annotations

import lightgbm as lgb
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    log_loss,
    roc_auc_score,
)

from app.ml.features import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    TARGET,
)


def prepare_lightgbm_features(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """Prepare numerical + one-hot categorical features for LightGBM."""

    feature_df = df[
        NUMERIC_FEATURES + CATEGORICAL_FEATURES
    ].copy()

    feature_df = pd.get_dummies(
        feature_df,
        columns=CATEGORICAL_FEATURES,
        dtype=float,
    )

    target = df[TARGET].astype(int)

    return feature_df, target


def train_lightgbm(
    train_df: pd.DataFrame,
) -> tuple[lgb.LGBMClassifier, list[str]]:
    """Train the LightGBM recovery probability model."""

    X_train, y_train = prepare_lightgbm_features(train_df)

    model = lgb.LGBMClassifier(
        objective="binary",
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=31,
        max_depth=-1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=-1,
    )

    model.fit(X_train, y_train)

    return model, list(X_train.columns)


def evaluate_lightgbm(
    model: lgb.LGBMClassifier,
    feature_columns: list[str],
    df: pd.DataFrame,
) -> dict[str, float]:
    """Evaluate the LightGBM model."""

    X, y = prepare_lightgbm_features(df)

    # Align validation/test columns to training columns.
    X = X.reindex(
        columns=feature_columns,
        fill_value=0,
    )

    probabilities = model.predict_proba(X)[:, 1]

    return {
        "roc_auc": roc_auc_score(y, probabilities),
        "pr_auc": average_precision_score(y, probabilities),
        "log_loss": log_loss(y, probabilities),
    }