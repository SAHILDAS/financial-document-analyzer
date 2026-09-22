from app.schemas.salary_analysis import SalaryAnalysisResult
from app.schemas.salary_slip import SalarySlip
from app.schemas.validation import ValidationResult
from app.services.analysis.salary_calculator import SalaryCalculator
from app.services.validation.confidence import SalaryConfidenceCalculator
from app.services.validation.salary_consistency import (
    SalaryConsistencyValidator,
)
from app.services.validation.salary_validator import SalaryValidator


class SalaryAnalysisService:
    """
    Orchestrate deterministic analysis of extracted salary data.

    Extraction is intentionally performed outside this service.
    This service receives an already extracted SalarySlip and
    determines whether the extracted information is internally
    consistent and trustworthy.
    """

    def __init__(
        self,
        calculator: SalaryCalculator | None = None,
        validator: SalaryValidator | None = None,
        consistency_validator: SalaryConsistencyValidator | None = None,
        confidence_calculator: SalaryConfidenceCalculator | None = None,
    ):
        self.calculator = calculator or SalaryCalculator()
        self.validator = validator or SalaryValidator()
        self.consistency_validator = (
            consistency_validator
            or SalaryConsistencyValidator()
        )
        self.confidence_calculator = (
            confidence_calculator
            or SalaryConfidenceCalculator()
        )

    def analyze(
        self,
        salary: SalarySlip,
        *,
        text_quality_score: float = 1.0,
    ) -> SalaryAnalysisResult:
        """Analyze an extracted salary slip."""

        domain_validation = self.validator.validate(salary)

        calculation = self.calculator.calculate(salary)

        consistency_validation = (
            self.consistency_validator.validate(calculation)
        )

        combined_validation = self._combine_validations(
            domain_validation,
            consistency_validation,
        )

        confidence = self.confidence_calculator.calculate(
            salary,
            combined_validation,
            text_quality_score=text_quality_score,
        )

        return SalaryAnalysisResult(
            salary=salary,
            calculation=calculation,
            validation=combined_validation,
            confidence=confidence,
        )

    @staticmethod
    def _combine_validations(
        domain_validation: ValidationResult,
        consistency_validation: ValidationResult,
    ) -> ValidationResult:
        return ValidationResult(
            is_valid=(
                domain_validation.is_valid
                and consistency_validation.is_valid
            ),
            issues=[
                *domain_validation.issues,
                *consistency_validation.issues,
            ],
        )