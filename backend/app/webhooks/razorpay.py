from __future__ import annotations

import hashlib
import hmac


def verify_razorpay_signature(
    *,
    payload: bytes,
    signature: str,
    secret: str,
) -> bool:
    """
    Verify a Razorpay webhook signature.

    Razorpay signs the raw request body using HMAC-SHA256.
    """

    expected_signature = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature,
    )