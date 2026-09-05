from __future__ import annotations

from dataclasses import dataclass

from app.decision.engine import ActionScore, choose_best_action
from app.policy.rules import (
    MIN_EXPECTED_VALUE_PAISE,
    is_action_allowed,
)


@dataclass(frozen=True)
class PolicyResult:
    selected_action: str
    reason: str
    scores: list[ActionScore]


def apply_policy(
    action_probabilities: dict[str, float],
    amount_paise: int,
    *,
    attempt_number: int,
    failure_code: str,
) -> PolicyResult:
    """
    Apply deterministic safety/eligibility rules and then
    optimize expected economic value.
    """

    eligible_probabilities: dict[str, float] = {}

    for action, probability in action_probabilities.items():
        policy = is_action_allowed(
            action=action,
            attempt_number=attempt_number,
            failure_code=failure_code,
            amount_paise=amount_paise,
        )

        if not policy.allowed:
            continue

        eligible_probabilities[action] = probability

    # Deterministic safety fallback.
    if not eligible_probabilities:
        return PolicyResult(
            selected_action="no_action",
            reason="all_actions_blocked",
            scores=[],
        )

    decision = choose_best_action(
        action_probabilities=eligible_probabilities,
        amount_paise=amount_paise,
    )

    selected_score = decision.scores[0]

    # Only the economic threshold can force NO_ACTION.
    if (
        selected_score.expected_value_paise
        < MIN_EXPECTED_VALUE_PAISE
        and selected_score.action != "no_action"
    ):
        return PolicyResult(
            selected_action="no_action",
            reason="expected_value_below_minimum",
            scores=decision.scores,
        )

    return PolicyResult(
        selected_action=selected_score.action,
        reason="best_eligible_expected_value",
        scores=decision.scores,
    )
