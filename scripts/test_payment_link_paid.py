from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

if not WEBHOOK_SECRET:
    raise RuntimeError(
        "RAZORPAY_WEBHOOK_SECRET is missing from .env"
    )


PAYMENT_LINK_ID = "plink_TYRIB1vdeUYJT9"

EVENT_ID = "revive-demo-payment-link-paid-002"

WEBHOOK_URL = "http://127.0.0.1:8000/webhooks/razorpay"


payload = {
    "entity": "event",
    "account_id": "acc_test_revive",
    "event": "payment_link.paid",
    "contains": [
        "payment_link",
        "payment",
    ],
    "payload": {
        "payment_link": {
            "entity": {
                "id": PAYMENT_LINK_ID,
                "amount": 250000,
                "amount_paid": 250000,
                "currency": "INR",
                "status": "paid",
            }
        },
        "payment": {
            "entity": {
                "id": "pay_revive_demo_002",
                "amount": 250000,
                "currency": "INR",
            }
        },
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


headers = {
    "Content-Type": "application/json",
    "X-Razorpay-Signature": signature,
    "X-Razorpay-Event-Id": EVENT_ID,
}


response = httpx.post(
    WEBHOOK_URL,
    content=raw_body,
    headers=headers,
    timeout=10.0,
)


print("Status:", response.status_code)
print("Response:", response.json())