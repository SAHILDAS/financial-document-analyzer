from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.salary_slip import SalarySlip
from app.services.extraction.llm_salary_extractor import (
    LlmSalaryExtractor,
)
from app.services.extraction.providers.mock_llm import MockLLMProvider
from app.services.extraction.salary_extractor import SalaryExtractionError


def create_salary_response() -> dict:
    return {
        "employee": {
            "name": "Test Employee",
            "employee_id": "EMP-001",
            "employer": "Example Technologies",
            "salary_month": "August 2026",
            "pan": None,
        },
        "earnings": {
            "basic": "40000",
            "hra": "15000",
            "allowances": "10000",
            "bonus": None,
            "other": None,
            "gross": "65000",
        },
        "deductions": {
            "pf": "4800",
            "professional_tax": None,
            "tds": "1200",
            "other": None,
            "total": "6000",
        },
        "net_salary": "59000",
        "bank_account": {
            "account_number": "XXXXXX1234",
        },
        "field_confidence": None,
    }


def test_llm_salary_extractor_returns_valid_salary_slip():
    provider = MockLLMProvider(create_salary_response())
    extractor = LlmSalaryExtractor(provider)

    result = extractor.extract(
        """
        Salary Slip
        Employee Name: Test Employee
        Employer: Example Technologies
        Gross Salary: 65000
        Total Deductions: 6000
        Net Salary: 59000
        """
    )

    assert isinstance(result, SalarySlip)
    assert result.employee.name == "Test Employee"
    assert result.earnings.gross == Decimal("65000")
    assert result.deductions.total == Decimal("6000")
    assert result.net_salary == Decimal("59000")


def test_llm_salary_extractor_preserves_missing_values():
    response = create_salary_response()

    response["earnings"]["bonus"] = None
    response["earnings"]["other"] = None
    response["deductions"]["professional_tax"] = None

    provider = MockLLMProvider(response)
    extractor = LlmSalaryExtractor(provider)

    result = extractor.extract("Salary Slip")

    assert result.earnings.bonus is None
    assert result.earnings.other is None
    assert result.deductions.professional_tax is None


def test_llm_salary_extractor_rejects_invalid_provider_response():
    response = create_salary_response()
    response["earnings"]["gross"] = "-100"

    provider = MockLLMProvider(response)
    extractor = LlmSalaryExtractor(provider)

    with pytest.raises(SalaryExtractionError):
        extractor.extract("Salary Slip")


def test_llm_salary_extractor_rejects_empty_text():
    provider = MockLLMProvider(create_salary_response())
    extractor = LlmSalaryExtractor(provider)

    with pytest.raises(SalaryExtractionError):
        extractor.extract("   ")


def test_llm_salary_extractor_hides_provider_failure():
    class FailingProvider(MockLLMProvider):
        def generate_structured(
            self,
            *,
            system_prompt: str,
            user_prompt: str,
            response_schema: dict,
        ) -> dict:
            raise RuntimeError("Provider connection failed")

    provider = FailingProvider({})
    extractor = LlmSalaryExtractor(provider)

    with pytest.raises(SalaryExtractionError):
        extractor.extract("Salary Slip")