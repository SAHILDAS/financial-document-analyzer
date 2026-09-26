from pydantic import BaseModel, Field

from app.schemas.bank_analysis_response import BankAnalysisResult
from app.schemas.reconciliation import ReconciliationResult
from app.schemas.salary_analysis import SalaryAnalysisResult


class ReconciliationRequest(BaseModel):
    """Structured salary and bank analysis results to reconcile."""

    salary: SalaryAnalysisResult
    bank: BankAnalysisResult


class ReconciliationResponse(BaseModel):
    """API response for salary-to-bank reconciliation."""

    success: bool
    result: ReconciliationResult | None = None
    error: str | None = None
