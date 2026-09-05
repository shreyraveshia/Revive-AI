from __future__ import annotations

import hashlib
import hmac

import httpx


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

    response = httpx.post(
        "http://127.0.0.1:8000/webhooks/razorpay",
        content=payload,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": signature,
        },
        timeout=10.0,
    )

    print("Status:", response.status_code)
    print("Response:", response.json())


if __name__ == "__main__":
    main()