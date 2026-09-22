from decimal import Decimal

from app.schemas.salary_calculation import SalaryCalculationResult
from app.schemas.validation import ValidationSeverity
from app.services.validation.salary_consistency import (
    SalaryConsistencyValidator,
)


def create_calculation(
    *,
    calculated_earnings: str | None = "65000",
    reported_gross: str | None = "65000",
    calculated_net: str | None = "59000",
    reported_net: str | None = "59000",
) -> SalaryCalculationResult:
    return SalaryCalculationResult(
        calculated_earnings=(
            Decimal(calculated_earnings)
            if calculated_earnings is not None
            else None
        ),
        reported_gross=(
            Decimal(reported_gross)
            if reported_gross is not None
            else None
        ),
        earnings_difference=(
            Decimal(calculated_earnings)
            - Decimal(reported_gross)
            if calculated_earnings is not None
            and reported_gross is not None
            else None
        ),
        calculated_net=(
            Decimal(calculated_net)
            if calculated_net is not None
            else None
        ),
        reported_net=(
            Decimal(reported_net)
            if reported_net is not None
            else None
        ),
        net_difference=(
            Decimal(calculated_net)
            - Decimal(reported_net)
            if calculated_net is not None
            and reported_net is not None
            else None
        ),
        can_calculate_earnings=(
            calculated_earnings is not None
        ),
        can_calculate_net=(
            calculated_net is not None
            and reported_gross is not None
        ),
    )


def test_valid_salary_has_no_consistency_issues():
    calculation = create_calculation()

    result = SalaryConsistencyValidator().validate(calculation)

    assert result.is_valid is True
    assert result.issues == []


def test_net_salary_mismatch_is_error():
    calculation = create_calculation(
        calculated_net="59000",
        reported_net="58000",
    )

    result = SalaryConsistencyValidator().validate(calculation)

    assert result.is_valid is False

    issue = next(
        issue
        for issue in result.issues
        if issue.code == "NET_SALARY_MISMATCH"
    )

    assert issue.severity == ValidationSeverity.ERROR
    assert issue.field == "net_salary"


def test_gross_salary_mismatch_is_error():
    calculation = create_calculation(
        calculated_earnings="67000",
        reported_gross="65000",
    )

    result = SalaryConsistencyValidator().validate(calculation)

    assert result.is_valid is False

    issue = next(
        issue
        for issue in result.issues
        if issue.code == "GROSS_SALARY_MISMATCH"
    )

    assert issue.severity == ValidationSeverity.ERROR
    assert issue.field == "earnings.gross"


def test_missing_earnings_component_creates_warning():
    calculation = create_calculation(
        calculated_earnings=None,
        reported_gross="65000",
    )

    result = SalaryConsistencyValidator().validate(calculation)

    assert result.is_valid is True

    assert any(
        issue.code == "GROSS_SALARY_NOT_FULLY_VERIFIABLE"
        and issue.severity == ValidationSeverity.WARNING
        for issue in result.issues
    )


def test_missing_net_values_create_warning():
    calculation = create_calculation(
        calculated_net=None,
        reported_net=None,
    )

    result = SalaryConsistencyValidator().validate(calculation)

    assert result.is_valid is True

    assert any(
        issue.code == "NET_SALARY_NOT_VERIFIABLE"
        and issue.severity == ValidationSeverity.WARNING
        for issue in result.issues
    )


def test_both_mismatches_are_reported():
    calculation = create_calculation(
        calculated_earnings="67000",
        reported_gross="65000",
        calculated_net="59000",
        reported_net="58000",
    )

    result = SalaryConsistencyValidator().validate(calculation)

    assert result.is_valid is False

    codes = {issue.code for issue in result.issues}

    assert "GROSS_SALARY_MISMATCH" in codes
    assert "NET_SALARY_MISMATCH" in codes


def test_one_dollar_rounding_difference_is_allowed():
    calculation = create_calculation(
        calculated_earnings="65000",
        reported_gross="65000.50",
        calculated_net="59000",
        reported_net="59000.50",
    )

    result = SalaryConsistencyValidator().validate(calculation)

    assert result.is_valid is True
    assert result.issues == []