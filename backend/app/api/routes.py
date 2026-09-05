from fastapi import APIRouter, HTTPException

from app.api.dashboard import get_metrics, get_recovery_actions
from app.api.schemas import (
    DemoFailedPaymentResponse,
    DemoFailedPaymentRequest,
    RecoveryDecisionRequest,
    RecoveryDecisionResponse,
    RecoveryExecutionRequest,
)
from app.api.service import (
    create_demo_failed_payment,
    decide_recovery,
    execute_recovery_payment_link,
)


router = APIRouter(
    prefix="/api",
    tags=["recovery"],
)



@router.post(
    "/demo/failed-payment",
    response_model=DemoFailedPaymentResponse,
)
def demo_failed_payment(request: DemoFailedPaymentRequest):
    try:
        return create_demo_failed_payment(
            amount_paise=request.amount_paise,
            payment_method=request.payment_method,
            failure_code=request.failure_code,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    

@router.get("/metrics")
def metrics():
    return get_metrics()


@router.get("/recovery/actions")
def recovery_actions(limit: int = 50):
    limit = max(1, min(limit, 100))
    return get_recovery_actions(limit)


@router.post(
    "/recovery/decide",
    response_model=RecoveryDecisionResponse,
)
def recovery_decision(request: RecoveryDecisionRequest):
    try:
        result, recovery_action = decide_recovery(request)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return RecoveryDecisionResponse(
        transaction_id=request.transaction_id,
        recovery_action_id=recovery_action.id,
        selected_action=result.policy_result.selected_action,
        decision_reason=result.policy_result.reason,
        diagnosis=result.diagnosis.model_dump(),
        action_scores=[
            score.__dict__
            for score in result.policy_result.scores
        ],
    )


@router.post("/recovery/execute")
def recovery_execute(request: RecoveryExecutionRequest):
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