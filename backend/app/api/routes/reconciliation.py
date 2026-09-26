from fastapi import APIRouter

from app.schemas.reconciliation import ReconciliationResult
from app.schemas.reconciliation_api import (
    ReconciliationRequest,
    ReconciliationResponse,
)
from app.services.reconciliation.reconciliation_service import (
    ReconciliationService,
)


router = APIRouter(
    prefix="/documents",
    tags=["Reconciliation"],
)


reconciliation_service = ReconciliationService()


@router.post(
    "/reconcile",
    response_model=ReconciliationResponse,
)
async def reconcile_documents(
    request: ReconciliationRequest,
) -> ReconciliationResponse:
    """
    Reconcile salary net pay against bank credit transactions.

    This endpoint consumes already-extracted structured data.
    No LLM call is performed here.
    """

    result: ReconciliationResult = (
        reconciliation_service.reconcile(
            salary=request.salary.salary,
            statement=request.bank.statement,
        )
    )

    return ReconciliationResponse(
        success=True,
        result=result,
    )
