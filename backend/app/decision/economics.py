from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionEconomics:
    fixed_cost_paise: int
    friction_penalty_paise: int
    risk_penalty_paise: int


ACTION_ECONOMICS: dict[str, ActionEconomics] = {
    "no_action": ActionEconomics(
        fixed_cost_paise=0,
        friction_penalty_paise=0,
        risk_penalty_paise=0,
    ),
    "retry": ActionEconomics(
        fixed_cost_paise=200,
        friction_penalty_paise=300,
        risk_penalty_paise=100,
    ),
    "alternate_method": ActionEconomics(
        fixed_cost_paise=150,
        friction_penalty_paise=250,
        risk_penalty_paise=100,
    ),
    "payment_link": ActionEconomics(
        fixed_cost_paise=100,
        friction_penalty_paise=150,
        risk_penalty_paise=50,
    ),
    "reminder": ActionEconomics(
        fixed_cost_paise=50,
        friction_penalty_paise=100,
        risk_penalty_paise=25,
    ),
    "escalate": ActionEconomics(
        fixed_cost_paise=500,
        friction_penalty_paise=350,
        risk_penalty_paise=200,
    ),
}


def calculate_expected_value(
    amount_paise: int,
    recovery_probability: float,
    action: str,
) -> float:
    """Calculate expected net recovered value for an action."""

    economics = ACTION_ECONOMICS[action]

    expected_recovery = (
        recovery_probability * amount_paise
    )

    total_cost = (
        economics.fixed_cost_paise
        + economics.friction_penalty_paise
        + economics.risk_penalty_paise
    )

    return expected_recovery - total_cost