from decimal import Decimal

from app.schemas.salary_calculation import SalaryCalculationResult
from app.schemas.validation import (
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)


class SalaryConsistencyValidator:
    """Validate deterministic relationships within salary data."""

    NET_TOLERANCE = Decimal("1.00")
    EARNINGS_TOLERANCE = Decimal("1.00")

    def validate(
        self,
        calculation: SalaryCalculationResult,
    ) -> ValidationResult:
        issues: list[ValidationIssue] = []

        self._validate_net_salary(calculation, issues)
        self._validate_earnings(calculation, issues)

        has_errors = any(
            issue.severity == ValidationSeverity.ERROR
            for issue in issues
        )

        return ValidationResult(
            is_valid=not has_errors,
            issues=issues,
        )

    def _validate_net_salary(
        self,
        calculation: SalaryCalculationResult,
        issues: list[ValidationIssue],
    ) -> None:
        if (
            calculation.calculated_net is None
            or calculation.reported_net is None
        ):
            issues.append(
                ValidationIssue(
                    code="NET_SALARY_NOT_VERIFIABLE",
                    message=(
                        "Net salary could not be fully verified "
                        "because required values are missing."
                    ),
                    severity=ValidationSeverity.WARNING,
                    field="net_salary",
                )
            )
            return

        difference = abs(
            calculation.calculated_net
            - calculation.reported_net
        )

        if difference > self.NET_TOLERANCE:
            issues.append(
                ValidationIssue(
                    code="NET_SALARY_MISMATCH",
                    message=(
                        "Calculated net salary does not match "
                        "the reported net salary."
                    ),
                    severity=ValidationSeverity.ERROR,
                    field="net_salary",
                )
            )

    def _validate_earnings(
        self,
        calculation: SalaryCalculationResult,
        issues: list[ValidationIssue],
    ) -> None:
        if (
            calculation.calculated_earnings is None
            or calculation.reported_gross is None
        ):
            issues.append(
                ValidationIssue(
                    code="GROSS_SALARY_NOT_FULLY_VERIFIABLE",
                    message=(
                        "Gross salary could not be fully verified "
                        "because one or more earning components "
                        "are missing."
                    ),
                    severity=ValidationSeverity.WARNING,
                    field="earnings.gross",
                )
            )
            return

        difference = abs(
            calculation.calculated_earnings
            - calculation.reported_gross
        )

        if difference > self.EARNINGS_TOLERANCE:
            issues.append(
                ValidationIssue(
                    code="GROSS_SALARY_MISMATCH",
                    message=(
                        "The sum of extracted earning components "
                        "does not match the reported gross salary."
                    ),
                    severity=ValidationSeverity.ERROR,
                    field="earnings.gross",
                )
            )