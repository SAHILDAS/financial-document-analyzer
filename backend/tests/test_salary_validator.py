from decimal import Decimal

from app.schemas.salary_slip import (
    SalaryDeductions,
    SalaryEarnings,
    SalaryEmployee,
    SalarySlip,
)
from app.schemas.validation import ValidationSeverity
from app.services.validation.salary_validator import SalaryValidator


def create_salary(
    *,
    gross: str | None = "65000",
    deductions: str | None = "6000",
    net: str | None = "59000",
) -> SalarySlip:
    return SalarySlip(
        employee=SalaryEmployee(
            name="Test Employee",
            employee_id="EMP-001",
            employer="Example Technologies",
            salary_month="August 2026",
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


def test_valid_salary_passes_validation():
    result = SalaryValidator().validate(create_salary())

    assert result.is_valid is True
    assert result.issues == []


def test_net_salary_mismatch_is_error():
    result = SalaryValidator().validate(
        create_salary(net="58000")
    )

    assert result.is_valid is False
    assert any(
        issue.code == "NET_SALARY_MISMATCH"
        and issue.severity == ValidationSeverity.ERROR
        for issue in result.issues
    )


def test_deductions_exceed_gross_is_error():
    result = SalaryValidator().validate(
        create_salary(
            gross="50000",
            deductions="55000",
            net="0",
        )
    )

    assert result.is_valid is False
    assert any(
        issue.code == "DEDUCTIONS_EXCEED_GROSS"
        for issue in result.issues
    )


def test_missing_gross_is_warning():
    result = SalaryValidator().validate(
        create_salary(gross=None)
    )

    assert result.is_valid is True
    assert any(
        issue.code == "MISSING_GROSS_SALARY"
        and issue.severity == ValidationSeverity.WARNING
        for issue in result.issues
    )


def test_missing_net_salary_is_warning():
    result = SalaryValidator().validate(
        create_salary(net=None)
    )

    assert result.is_valid is True
    assert any(
        issue.code == "MISSING_NET_SALARY"
        and issue.severity == ValidationSeverity.WARNING
        for issue in result.issues
    )


def test_small_rounding_difference_is_allowed():
    result = SalaryValidator().validate(
        create_salary(net="59000.50")
    )

    assert result.is_valid is True
    assert result.issues == []


def test_missing_values_are_not_treated_as_zero():
    result = SalaryValidator().validate(
        create_salary(
            gross=None,
            deductions=None,
            net=None,
        )
    )

    assert result.is_valid is True

    codes = {issue.code for issue in result.issues}

    assert "MISSING_GROSS_SALARY" in codes
    assert "MISSING_TOTAL_DEDUCTIONS" in codes
    assert "MISSING_NET_SALARY" in codes