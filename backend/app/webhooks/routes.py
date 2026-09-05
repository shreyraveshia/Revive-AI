from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.recovery_action import RecoveryAction
from app.models.recovery_outcome import RecoveryOutcome
from app.models.webhook_event import WebhookEvent
from app.webhooks.razorpay import verify_razorpay_signature


router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
    x_razorpay_event_id: str | None = Header(default=None),
) -> dict[str, str]:

    settings = get_settings()

    if not x_razorpay_signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay webhook signature.",
        )

    if not x_razorpay_event_id:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay event ID.",
        )

    if not settings.razorpay_webhook_secret:
        raise HTTPException(
            status_code=500,
            detail="Razorpay webhook secret is not configured.",
        )

    raw_body = await request.body()

    if not verify_razorpay_signature(
        payload=raw_body,
        signature=x_razorpay_signature,
        secret=settings.razorpay_webhook_secret,
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid Razorpay webhook signature.",
        )

    try:
        event = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON webhook payload.",
        ) from exc

    event_type = event.get("event")

    db = SessionLocal()

    try:
        existing_event = db.scalar(
            select(WebhookEvent).where(
                WebhookEvent.event_id == x_razorpay_event_id
            )
        )

        if existing_event is not None:
            return {
                "status": "duplicate_ignored",
                "event": event_type or "unknown",
            }

        webhook_record = WebhookEvent(
            provider="razorpay",
            event_id=x_razorpay_event_id,
            event_type=event_type or "unknown",
            payload=raw_body.decode("utf-8"),
        )

        db.add(webhook_record)

        if event_type == "payment_link.paid":
            payment_link_entity = (
                event.get("payload", {})
                .get("payment_link", {})
                .get("entity", {})
            )

            payment_link_id = payment_link_entity.get("id")

            if not payment_link_id:
                raise HTTPException(
                    status_code=400,
                    detail="Payment Link ID missing from webhook.",
                )

            action = db.scalar(
                select(RecoveryAction).where(
                    RecoveryAction.external_reference
                    == payment_link_id
                )
            )

            if action is None:
                raise HTTPException(
                    status_code=404,
                    detail="RecoveryAction not found for Payment Link.",
                )

            existing_outcome = db.scalar(
                select(RecoveryOutcome).where(
                    RecoveryOutcome.recovery_action_id == action.id
                )
            )

            if existing_outcome is None:
                amount = payment_link_entity.get("amount", 0)

                outcome = RecoveryOutcome(
                    recovery_action_id=action.id,
                    status="RECOVERED",
                    amount_recovered_paise=int(amount),
                    external_reference=payment_link_id,
                    notes="Payment recovered through Razorpay Payment Link.",
                    completed_at=datetime.now(timezone.utc),
                )

                db.add(outcome)

                action.status = "EXECUTED"

        db.commit()

        return {
            "status": "accepted",
            "event": event_type or "unknown",
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()