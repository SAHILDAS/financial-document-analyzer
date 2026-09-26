from decimal import Decimal

from app.schemas.salary_slip import (
    SalaryDeductions,
    SalaryEarnings,
    SalaryEmployee,
    SalarySlip,
)
from app.services.analysis.salary_calculator import SalaryCalculator


def create_salary(
    *,
    bonus: str | None = "0",
    other: str | None = "0",
    gross: str = "65000",
    deductions: str = "6000",
    net: str = "59000",
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
            bonus=(
                Decimal(bonus)
                if bonus is not None
                else None
            ),
            other=(
                Decimal(other)
                if other is not None
                else None
            ),
            gross=Decimal(gross),
        ),
        deductions=SalaryDeductions(
            pf=Decimal("4800"),
            tds=Decimal("1200"),
            total=Decimal(deductions),
        ),
        net_salary=Decimal(net),
    )


def test_calculates_earnings_from_all_components():
    salary = create_salary(
        bonus="2000",
        other="1000",
        gross="68000",
    )

    result = SalaryCalculator().calculate(salary)

    assert result.can_calculate_earnings is True
    assert result.calculated_earnings == Decimal("68000")
    assert result.reported_gross == Decimal("68000")
    assert result.earnings_difference == Decimal("0")


def test_detects_earnings_difference():
    salary = create_salary(
        bonus="1000",
        other="500",
        gross="65000",
    )

    result = SalaryCalculator().calculate(salary)

    assert result.can_calculate_earnings is True
    assert result.calculated_earnings == Decimal("66500")
    assert result.earnings_difference == Decimal("1500")


def test_calculates_expected_net_salary():
    salary = create_salary(
        gross="65000",
        deductions="6000",
        net="59000",
    )

    result = SalaryCalculator().calculate(salary)

    assert result.can_calculate_net is True
    assert result.calculated_net == Decimal("59000")
    assert result.reported_net == Decimal("59000")
    assert result.net_difference == Decimal("0")


def test_detects_net_salary_difference():
    salary = create_salary(
        gross="65000",
        deductions="6000",
        net="58000",
    )

    result = SalaryCalculator().calculate(salary)

    assert result.calculated_net == Decimal("59000")
    assert result.reported_net == Decimal("58000")
    assert result.net_difference == Decimal("1000")


def test_missing_bonus_still_allows_available_earnings_calculation():
    salary = create_salary(
        bonus=None,
        other="1000",
        gross="66000",
    )

    result = SalaryCalculator().calculate(salary)

    assert result.can_calculate_earnings is True
    assert result.calculated_earnings == Decimal("66000")
    assert result.reported_gross == Decimal("66000")
    assert result.earnings_difference == Decimal("0")


def test_missing_other_earnings_still_allows_available_earnings_calculation():
    salary = create_salary(
        bonus="1000",
        other=None,
        gross="66000",
    )

    result = SalaryCalculator().calculate(salary)

    assert result.can_calculate_earnings is True
    assert result.calculated_earnings == Decimal("66000")
    assert result.reported_gross == Decimal("66000")
    assert result.earnings_difference == Decimal("0")


def test_net_calculation_does_not_require_individual_deductions():
    salary = create_salary(
        gross="65000",
        deductions="6000",
        net="59000",
    )

    result = SalaryCalculator().calculate(salary)

    assert result.can_calculate_net is True
    assert result.calculated_net == Decimal("59000")



def test_calculates_gross_from_partial_realistic_earning_components():
    salary = SalarySlip(
        employee=SalaryEmployee(
            name="Sanjib Das",
            employee_id="Emp101",
            employer="demo company 101",
            salary_month="Sep 2026",
        ),
        earnings=SalaryEarnings(
            basic=Decimal("45000"),
            hra=Decimal("10000"),
            allowances=None,
            bonus=None,
            other=Decimal("1000"),
            gross=Decimal("56000"),
        ),
        deductions=SalaryDeductions(
            pf=Decimal("4500"),
            tds=Decimal("1000"),
            total=Decimal("5500"),
        ),
        net_salary=Decimal("50500"),
    )

    result = SalaryCalculator().calculate(salary)

    assert result.can_calculate_earnings is True
    assert result.calculated_earnings == Decimal("56000")
    assert result.reported_gross == Decimal("56000")
    assert result.earnings_difference == Decimal("0")

    assert result.can_calculate_net is True
    assert result.calculated_net == Decimal("50500")
    assert result.reported_net == Decimal("50500")
    assert result.net_difference == Decimal("0")
