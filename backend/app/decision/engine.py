from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionScore:
    action: str
    recovery_probability: float
    expected_value_paise: float


@dataclass(frozen=True)
class Decision:
    selected_action: str
    scores: list[ActionScore]


def choose_best_action(
    action_probabilities: dict[str, float],
    amount_paise: int,
) -> Decision:
    """Choose the action with the highest expected value."""

    from app.decision.economics import calculate_expected_value

    scores: list[ActionScore] = []

    for action, probability in action_probabilities.items():
        expected_value = calculate_expected_value(
            amount_paise=amount_paise,
            recovery_probability=probability,
            action=action,
        )

        scores.append(
            ActionScore(
                action=action,
                recovery_probability=probability,
                expected_value_paise=expected_value,
            )
        )

    scores.sort(
        key=lambda score: score.expected_value_paise,
        reverse=True,
    )

    return Decision(
        selected_action=scores[0].action,
        scores=scores,
    )