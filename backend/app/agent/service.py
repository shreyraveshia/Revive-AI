from __future__ import annotations

from dataclasses import dataclass

import lightgbm as lgb
import pandas as pd

from app.agent.context import RecoveryContext
from app.llm.safe_provider import SafeLLMProvider
from app.ml.lightgbm_model import prepare_lightgbm_features
from app.policy.engine import PolicyResult, apply_policy


@dataclass(frozen=True)
class AgentDecision:
    diagnosis: object
    policy_result: PolicyResult


class ReviveAgent:
    """
    Orchestrates diagnosis, recovery prediction, decisioning,
    and policy enforcement.

    The agent does not execute payments.
    """

    def __init__(
        self,
        recovery_model: lgb.LGBMClassifier,
        feature_columns: list[str],
    ) -> None:
        self.recovery_model = recovery_model
        self.feature_columns = feature_columns
        self.llm = SafeLLMProvider()

    def decide(
        self,
        context: RecoveryContext,
    ) -> AgentDecision:
        diagnosis = self.llm.diagnose_failure(
            transaction_amount_paise=context.amount_paise,
            payment_method=context.payment_method,
            failure_code=context.failure_code,
            attempt_number=context.attempt_number,
            customer_previous_transactions=(
                context.customer_previous_transactions
            ),
            customer_previous_success_rate=(
                context.customer_previous_success_rate
            ),
            merchant_previous_success_rate=(
                context.merchant_previous_success_rate
            ),
        )

        action_rows = []

        for action in [
            "no_action",
            "retry",
            "alternate_method",
            "payment_link",
            "reminder",
            "escalate",
        ]:
            action_rows.append(
                {
                    "amount_paise": context.amount_paise,
                    "payment_method": context.payment_method,
                    "failure_code": context.failure_code,
                    "customer_previous_transactions": (
                        context.customer_previous_transactions
                    ),
                    "customer_previous_success_rate": (
                        context.customer_previous_success_rate
                    ),
                    "customer_previous_avg_amount_paise": (
                        context.customer_previous_avg_amount_paise
                    ),
                    "merchant_previous_transactions": (
                        context.merchant_previous_transactions
                    ),
                    "merchant_previous_success_rate": (
                        context.merchant_previous_success_rate
                    ),
                    "merchant_previous_avg_amount_paise": (
                        context.merchant_previous_avg_amount_paise
                    ),
                    "action": action,
                }
            )

        action_df = pd.DataFrame(action_rows)

        X, _ = prepare_lightgbm_features(
            pd.DataFrame(
                {
                    **{
                        column: action_df[column]
                        for column in action_df.columns
                    },
                    "recovered": 0,
                }
            )
        )

        X = X.reindex(
            columns=self.feature_columns,
            fill_value=0,
        )

        probabilities_array = (
            self.recovery_model.predict_proba(X)[:, 1]
        )

        probabilities = {
            action: float(probability)
            for action, probability in zip(
                action_df["action"],
                probabilities_array,
            )
        }

        policy_result = apply_policy(
            action_probabilities=probabilities,
            amount_paise=context.amount_paise,
            attempt_number=context.attempt_number,
            failure_code=context.failure_code,
        )

        return AgentDecision(
            diagnosis=diagnosis,
            policy_result=policy_result,
        )