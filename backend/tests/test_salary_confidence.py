from decimal import Decimal

from app.schemas.salary_slip import (
    SalaryDeductions,
    SalaryEarnings,
    SalaryEmployee,
    SalarySlip,
)
from app.schemas.validation import (
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)
from app.services.validation.confidence import (
    SalaryConfidenceCalculator,
)


def create_salary(
    *,
    employer: str | None = "Example Technologies",
    salary_month: str | None = "August 2026",
    gross: str | None = "65000",
    deductions: str | None = "6000",
    net: str | None = "59000",
) -> SalarySlip:
    return SalarySlip(
        employee=SalaryEmployee(
            name="Test Employee",
            employee_id="EMP-001",
            employer=employer,
            salary_month=salary_month,
        ),
        earnings=SalaryEarnings(
            basic=Decimal("40000"),
            hra=Decimal("15000"),
            allowances=Decimal("10000"),
            gross=(
                Decimal(gross)
                if gross is not None
                else None
            ),
        ),
        deductions=SalaryDeductions(
            pf=Decimal("4800"),
            tds=Decimal("1200"),
            total=(
                Decimal(deductions)
                if deductions is not None
                else None
            ),
        ),
        net_salary=(
            Decimal(net)
            if net is not None
            else None
        ),
    )


def test_complete_consistent_salary_has_high_confidence():
    salary = create_salary()

    validation = ValidationResult(
        is_valid=True,
        issues=[],
    )

    result = SalaryConfidenceCalculator().calculate(
        salary,
        validation,
        text_quality_score=0.95,
    )

    assert result.score >= 0.85
    assert result.level.value == "high"
    assert result.needs_review is False


def test_moderate_text_quality_reduces_confidence():
    salary = create_salary()

    validation = ValidationResult(
        is_valid=True,
        issues=[],
    )

    result = SalaryConfidenceCalculator().calculate(
        salary,
        validation,
        text_quality_score=0.75,
    )

    assert result.score < 1.0
    assert "moderate" in result.reasons[0].lower()


def test_missing_fields_reduce_confidence():
    salary = create_salary(
        employer=None,
        salary_month=None,
        gross=None,
        deductions=None,
        net=None,
    )

    validation = ValidationResult(
        is_valid=True,
        issues=[],
    )

    result = SalaryConfidenceCalculator().calculate(
        salary,
        validation,
        text_quality_score=0.95,
    )

    assert result.score < 0.85
    assert any(
        "missing" in reason.lower()
        for reason in result.reasons
    )


def test_validation_warning_reduces_confidence():
    salary = create_salary()

    validation = ValidationResult(
        is_valid=True,
        issues=[
            ValidationIssue(
                code="MISSING_FIELD",
                message="Field is missing.",
                severity=ValidationSeverity.WARNING,
                field="employee.employee_id",
            )
        ],
    )

    result = SalaryConfidenceCalculator().calculate(
        salary,
        validation,
        text_quality_score=0.95,
    )

    assert result.score < 1.0
    assert any(
        "warning" in reason.lower()
        for reason in result.reasons
    )


def test_validation_error_requires_review():
    salary = create_salary()

    validation = ValidationResult(
        is_valid=False,
        issues=[
            ValidationIssue(
                code="NET_SALARY_MISMATCH",
                message="Net salary mismatch.",
                severity=ValidationSeverity.ERROR,
                field="net_salary",
            )
        ],
    )

    result = SalaryConfidenceCalculator().calculate(
        salary,
        validation,
        text_quality_score=0.95,
    )

    assert result.needs_review is True
    assert any(
        "error" in reason.lower()
        for reason in result.reasons
    )


def test_low_text_quality_can_trigger_review():
    salary = create_salary()

    validation = ValidationResult(
        is_valid=True,
        issues=[],
    )

    result = SalaryConfidenceCalculator().calculate(
        salary,
        validation,
        text_quality_score=0.20,
    )

    assert result.level.value == "medium" or result.level.value == "low"

    if result.level.value == "low":
        assert result.needs_review is True


def test_confidence_score_is_bounded():
    salary = create_salary(
        employer=None,
        salary_month=None,
        gross=None,
        deductions=None,
        net=None,
    )

    validation = ValidationResult(
        is_valid=False,
        issues=[
            ValidationIssue(
                code="ERROR_ONE",
                message="Error.",
                severity=ValidationSeverity.ERROR,
            ),
            ValidationIssue(
                code="ERROR_TWO",
                message="Error.",
                severity=ValidationSeverity.ERROR,
            ),
        ],
    )

    result = SalaryConfidenceCalculator().calculate(
        salary,
        validation,
        text_quality_score=0.0,
    )

    assert 0.0 <= result.score <= 1.0