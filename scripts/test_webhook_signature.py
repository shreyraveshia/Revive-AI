from __future__ import annotations

import hashlib
import hmac

from app.webhooks.razorpay import verify_razorpay_signature


def main() -> None:
    secret = "revive-test-webhook-secret"

    payload = (
        b'{"event":"payment_link.paid",'
        b'"payload":{"payment_link":{"entity":{"id":"plink_test"}}}}'
    )

    signature = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    valid = verify_razorpay_signature(
        payload=payload,
        signature=signature,
        secret=secret,
    )

    invalid = verify_razorpay_signature(
        payload=payload,
        signature="invalid-signature",
        secret=secret,
    )

    print("Valid signature:", valid)
    print("Invalid signature:", invalid)


if __name__ == "__main__":
    main()