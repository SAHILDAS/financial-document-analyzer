from pydantic import BaseModel

from app.schemas.confidence import ConfidenceResult
from app.schemas.salary_calculation import SalaryCalculationResult
from app.schemas.salary_slip import SalarySlip
from app.schemas.validation import ValidationResult


class SalaryAnalysisResult(BaseModel):
    """Complete deterministic analysis result for a salary document."""

    salary: SalarySlip
    calculation: SalaryCalculationResult
    validation: ValidationResult
    confidence: ConfidenceResult