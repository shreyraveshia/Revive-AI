from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyDecision:
    action: str
    allowed: bool
    reason: str


MAX_RETRY_ATTEMPTS = 2
MIN_EXPECTED_VALUE_PAISE = 500
MIN_CONFIDENCE_FOR_ACTION = 0.55

HIGH_VALUE_THRESHOLD_PAISE = 500_000
HIGH_VALUE_ESCALATION_THRESHOLD_PAISE = 1_500_000


def is_retry_allowed(
    attempt_number: int,
    failure_code: str,
) -> PolicyDecision:
    """
    Determine whether another retry is permitted.

    Retry is intentionally bounded.
    """

    if attempt_number > MAX_RETRY_ATTEMPTS:
        return PolicyDecision(
            action="retry",
            allowed=False,
            reason="retry_limit_exceeded",
        )

    hard_failures = {
        "hard_decline",
        "authentication_failed",
    }

    if failure_code in hard_failures:
        return PolicyDecision(
            action="retry",
            allowed=False,
            reason="failure_type_not_retryable",
        )

    return PolicyDecision(
        action="retry",
        allowed=True,
        reason="retry_allowed",
    )


def is_action_allowed(
    action: str,
    *,
    attempt_number: int,
    failure_code: str,
    amount_paise: int,
) -> PolicyDecision:
    """
    Apply deterministic eligibility rules to a candidate action.
    """

    if action == "retry":
        return is_retry_allowed(
            attempt_number=attempt_number,
            failure_code=failure_code,
        )

    if action == "escalate":
        if amount_paise < HIGH_VALUE_THRESHOLD_PAISE:
            return PolicyDecision(
                action=action,
                allowed=False,
                reason="amount_below_escalation_threshold",
            )

    if action == "no_action":
        return PolicyDecision(
            action=action,
            allowed=True,
            reason="always_allowed",
        )

    return PolicyDecision(
        action=action,
        allowed=True,
        reason="action_allowed",
    )