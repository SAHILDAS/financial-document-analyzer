from decimal import Decimal

from app.schemas.salary_slip import SalarySlip
from app.schemas.validation import (
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)


class SalaryValidator:
    """Validate salary-slip data using deterministic business rules."""

    NET_TOLERANCE = Decimal("1.00")

    def validate(self, salary: SalarySlip) -> ValidationResult:
        issues: list[ValidationIssue] = []

        self._validate_required_structure(salary, issues)
        self._validate_totals(salary, issues)
        self._validate_net_salary(salary, issues)

        has_errors = any(
            issue.severity == ValidationSeverity.ERROR
            for issue in issues
        )

        return ValidationResult(
            is_valid=not has_errors,
            issues=issues,
        )

    @staticmethod
    def _validate_required_structure(
        salary: SalarySlip,
        issues: list[ValidationIssue],
    ) -> None:
        if salary.employee.name is None:
            issues.append(
                ValidationIssue(
                    code="MISSING_EMPLOYEE_NAME",
                    message="Employee name is missing.",
                    severity=ValidationSeverity.WARNING,
                    field="employee.name",
                )
            )

        if salary.employee.employer is None:
            issues.append(
                ValidationIssue(
                    code="MISSING_EMPLOYER",
                    message="Employer name is missing.",
                    severity=ValidationSeverity.WARNING,
                    field="employee.employer",
                )
            )

        if salary.earnings.gross is None:
            issues.append(
                ValidationIssue(
                    code="MISSING_GROSS_SALARY",
                    message="Gross salary is missing.",
                    severity=ValidationSeverity.WARNING,
                    field="earnings.gross",
                )
            )

        if salary.deductions.total is None:
            issues.append(
                ValidationIssue(
                    code="MISSING_TOTAL_DEDUCTIONS",
                    message="Total deductions are missing.",
                    severity=ValidationSeverity.WARNING,
                    field="deductions.total",
                )
            )

        if salary.net_salary is None:
            issues.append(
                ValidationIssue(
                    code="MISSING_NET_SALARY",
                    message="Net salary is missing.",
                    severity=ValidationSeverity.WARNING,
                    field="net_salary",
                )
            )

    def _validate_totals(
        self,
        salary: SalarySlip,
        issues: list[ValidationIssue],
    ) -> None:
        gross = salary.earnings.gross
        deductions = salary.deductions.total

        if gross is None or deductions is None:
            return

        expected_net = gross - deductions

        if expected_net < Decimal("0"):
            issues.append(
                ValidationIssue(
                    code="DEDUCTIONS_EXCEED_GROSS",
                    message=(
                        "Total deductions exceed gross salary."
                    ),
                    severity=ValidationSeverity.ERROR,
                    field="deductions.total",
                )
            )

    def _validate_net_salary(
        self,
        salary: SalarySlip,
        issues: list[ValidationIssue],
    ) -> None:
        gross = salary.earnings.gross
        deductions = salary.deductions.total
        net = salary.net_salary

        if gross is None or deductions is None or net is None:
            return

        expected_net = gross - deductions
        difference = abs(expected_net - net)

        if difference > self.NET_TOLERANCE:
            issues.append(
                ValidationIssue(
                    code="NET_SALARY_MISMATCH",
                    message=(
                        "Gross salary minus total deductions does not "
                        "match the reported net salary."
                    ),
                    severity=ValidationSeverity.ERROR,
                    field="net_salary",
                )
            )