from pydantic import BaseModel

from app.schemas.bank_analysis import BankFinancialAnalysis
from app.schemas.bank_statement import BankStatement
from app.schemas.bank_validation import BankValidationResult


class BankAnalysisResult(BaseModel):
    """Complete deterministic analysis result for a bank statement."""

    statement: BankStatement
    analysis: BankFinancialAnalysis
    validation: BankValidationResult