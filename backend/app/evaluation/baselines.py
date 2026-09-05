from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BaselineResult:
    name: str
    transactions_evaluated: int
    revenue_at_risk_paise: int
    recovered_revenue_paise: int

    @property
    def recovery_rate(self) -> float:
        if self.revenue_at_risk_paise == 0:
            return 0.0

        return (
            self.recovered_revenue_paise
            / self.revenue_at_risk_paise
        )

    @property
    def recovered_revenue_rupees(self) -> float:
        return self.recovered_revenue_paise / 100

    @property
    def revenue_at_risk_rupees(self) -> float:
        return self.revenue_at_risk_paise / 100


def _transaction_level_revenue_at_risk(
    df: pd.DataFrame,
) -> int:
    """
    Calculate revenue at risk once per transaction.

    The action-level dataset contains six rows per transaction,
    so we must not sum `amount_paise` directly across action rows.
    """

    return int(
        df[
            ["transaction_id", "amount_paise"]
        ]
        .drop_duplicates("transaction_id")["amount_paise"]
        .sum()
    )


def evaluate_action_baseline(
    test_df: pd.DataFrame,
    action: str,
    name: str,
) -> BaselineResult:
    """
    Evaluate a strategy that always chooses one action.

    Example:
        action="retry" → blind retry
        action="no_action" → no-action baseline
    """

    action_df = test_df[
        test_df["action"] == action
    ].copy()

    transactions = action_df["transaction_id"].nunique()

    revenue_at_risk = _transaction_level_revenue_at_risk(
        action_df
    )

    recovered_revenue = int(
        action_df["recovered_amount_paise"].sum()
    )

    return BaselineResult(
        name=name,
        transactions_evaluated=transactions,
        revenue_at_risk_paise=revenue_at_risk,
        recovered_revenue_paise=recovered_revenue,
    )


def evaluate_baselines(
    test_df: pd.DataFrame,
) -> list[BaselineResult]:
    """Evaluate the initial no-action and blind-retry baselines."""

    return [
        evaluate_action_baseline(
            test_df,
            action="no_action",
            name="NO_ACTION",
        ),
        evaluate_action_baseline(
            test_df,
            action="retry",
            name="BLIND_RETRY",
        ),
    ]