from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.ml.features import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    prepare_features,
)


@dataclass(frozen=True)
class ModelMetrics:
    roc_auc: float
    pr_auc: float
    log_loss: float


def build_logistic_regression() -> Pipeline:
    """
    Build an interpretable probability model.

    Numeric features are standardized.
    Categorical features use one-hot encoding.
    """

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                StandardScaler(),
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                ),
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    model = LogisticRegression(
        max_iter=1_000,
        class_weight="balanced",
        random_state=42,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def evaluate_model(
    model: Pipeline,
    df: pd.DataFrame,
) -> ModelMetrics:
    """Evaluate probability quality on a dataset."""

    X, y = prepare_features(df)

    probabilities = model.predict_proba(X)[:, 1]

    return ModelMetrics(
        roc_auc=roc_auc_score(y, probabilities),
        pr_auc=average_precision_score(y, probabilities),
        log_loss=log_loss(y, probabilities),
    )