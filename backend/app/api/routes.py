from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    RecoveryDecisionRequest,
    RecoveryDecisionResponse,
    RecoveryExecutionRequest,
)
from app.api.service import (
    decide_recovery,
    execute_recovery_payment_link,
)


router = APIRouter(
    prefix="/api",
    tags=["recovery"],
)


@router.post(
    "/recovery/decide",
    response_model=RecoveryDecisionResponse,
)
def recovery_decision(
    request: RecoveryDecisionRequest,
) -> RecoveryDecisionResponse:

    try:
        result = decide_recovery(request)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return RecoveryDecisionResponse(
        transaction_id=request.transaction_id,
        selected_action=result.policy_result.selected_action,
        decision_reason=result.policy_result.reason,
        diagnosis=result.diagnosis.model_dump(),
        action_scores=[
            score.__dict__
            for score in result.policy_result.scores
        ],
    )


@router.post("/recovery/execute")
def recovery_execute(
    request: RecoveryExecutionRequest,
):
    try:
        result = execute_recovery_payment_link(
            recovery_action_id=request.recovery_action_id,
            amount_paise=request.amount_paise,
            reference_id=request.reference_id,
            description=request.description,
            customer_name=request.customer_name,
            customer_email=request.customer_email,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return result.model_dump()