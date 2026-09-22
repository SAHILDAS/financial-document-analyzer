from app.services.extraction.llm_salary_extractor import (
    LlmSalaryExtractor,
)
from app.services.extraction.providers.mock_llm import MockLLMProvider


def create_salary_extractor() -> LlmSalaryExtractor:
    """
    Create the configured salary extractor.

    The prototype currently uses a deterministic mock provider.
    A real LLM provider can replace this factory implementation
    without changing the extraction or analysis contracts.
    """

    provider = MockLLMProvider(
        {
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
                "bonus": "0",
                "other": "0",
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
    )

    return LlmSalaryExtractor(provider)
