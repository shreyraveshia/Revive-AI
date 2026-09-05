from __future__ import annotations

import pandas as pd


def choose_rule_based_action(row: pd.Series) -> str:
    """Choose a recovery action using simple deterministic rules."""

    failure_code = row["failure_code"]

    if failure_code in {
        "upi_timeout",
        "network_error",
        "gateway_error",
        "soft_decline",
    }:
        return "retry"

    if failure_code == "insufficient_funds":
        return "reminder"

    if failure_code == "checkout_abandoned":
        return "payment_link"

    if failure_code in {
        "hard_decline",
        "authentication_failed",
        "upi_declined",
    }:
        return "alternate_method"

    return "no_action"