from enum import StrEnum


class TransactionStatus(StrEnum):
    CREATED = "created"
    FAILED = "failed"
    SUCCESS = "success"
    RECOVERED = "recovered"


class PaymentMethod(StrEnum):
    UPI = "upi"
    CARD = "card"
    NETBANKING = "netbanking"
    WALLET = "wallet"


class PaymentAttemptStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"


class FailureCode(StrEnum):
    UPI_TIMEOUT = "upi_timeout"
    UPI_DECLINED = "upi_declined"

    INSUFFICIENT_FUNDS = "insufficient_funds"
    HARD_DECLINE = "hard_decline"
    SOFT_DECLINE = "soft_decline"

    NETWORK_ERROR = "network_error"
    GATEWAY_ERROR = "gateway_error"

    AUTHENTICATION_FAILED = "authentication_failed"
    CHECKOUT_ABANDONED = "checkout_abandoned"


class RecoveryActionType(StrEnum):
    NO_ACTION = "no_action"
    RETRY = "retry"
    ALTERNATE_METHOD = "alternate_method"
    PAYMENT_LINK = "payment_link"
    REMINDER = "reminder"
    ESCALATE = "escalate"


class RecoveryActionStatus(StrEnum):
    PROPOSED = "proposed"
    EXECUTED = "executed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class RecoveryOutcomeStatus(StrEnum):
    RECOVERED = "recovered"
    NOT_RECOVERED = "not_recovered"
    EXPIRED = "expired"