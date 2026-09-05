from __future__ import annotations

import hashlib
import hmac
import json

import httpx


WEBHOOK_SECRET = "revive-test-webhook-secret"
PAYMENT_LINK_ID = "plink_TYPLEAF7p5G1kR"
EVENT_ID = "revive-test-event-001"


def main() -> None:
    payload = {
        "event": "payment_link.paid",
        "payload": {
            "payment_link": {
                "entity": {
                    "id": PAYMENT_LINK_ID,
                    "amount": 10000,
                    "status": "paid",
                }
            }
        },
    }

    raw_body = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode("utf-8")

    signature = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    response = httpx.post(
        "http://127.0.0.1:8000/webhooks/razorpay",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": signature,
            "X-Razorpay-Event-Id": EVENT_ID,
        },
        timeout=10.0,
    )

    print("Status:", response.status_code)
    print("Response:", response.json())


if __name__ == "__main__":
    main()