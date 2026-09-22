from decimal import Decimal

import pytest

from app.schemas.salary_slip import SalarySlip
from app.services.extraction.providers.mock import MockSalaryExtractor


def test_mock_salary_extractor_returns_salary_slip():
    extractor = MockSalaryExtractor()

    result = extractor.extract(
        """
        Salary Slip
        Employee Name: Test Employee
        Employee ID: EMP-001
        Employer: Example Technologies
        Salary Month: August 2026

        Basic Salary: 40000
        HRA: 15000
        Allowances: 10000
        Gross Salary: 65000

        PF: 4800
        TDS: 1200
        Total Deductions: 6000

        Net Salary: 59000
        """
    )

    assert isinstance(result, SalarySlip)
    assert result.employee.name == "Test Employee"
    assert result.earnings.gross == Decimal("65000")
    assert result.deductions.total == Decimal("6000")
    assert result.net_salary == Decimal("59000")


def test_mock_salary_extractor_result_allows_missing_optional_values():
    extractor = MockSalaryExtractor()

    result = extractor.extract(
        """
        Salary Slip
        Employee Name: Test Employee
        """
    )

    assert result.deductions.professional_tax is None
    assert result.deductions.other is None


def test_mock_salary_extractor_rejects_non_salary_text():
    extractor = MockSalaryExtractor()

    with pytest.raises(ValueError):
        extractor.extract(
            """
            Bank Statement
            Account Number: 123456789
            Opening Balance: 50000
            Closing Balance: 60000
            """
        )