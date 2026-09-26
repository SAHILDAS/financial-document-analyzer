from app.core.config import settings
from app.services.extraction.llm_bank_extractor import (
    LlmBankExtractor,
)
from app.services.extraction.llm_salary_extractor import (
    LlmSalaryExtractor,
)
from app.services.extraction.providers.mock_llm import (
    MockLLMProvider,
)
from app.services.extraction.providers.openai_provider import (
    OpenAIProvider,
)


def create_salary_extractor() -> LlmSalaryExtractor:
    """
    Create the configured salary extractor.

    Production/runtime extraction uses the configured LLM provider.

    Mock extraction remains available for deterministic tests by
    directly constructing MockLLMProvider in test code.
    """

    if settings.llm_provider == "openai":
        provider = OpenAIProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
    else:
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


def create_bank_extractor() -> LlmBankExtractor:
    """
    Create the configured bank statement extractor.

    Production/runtime extraction uses the configured LLM provider.

    Mock extraction remains available for deterministic tests by
    directly constructing MockLLMProvider in test code.
    """

    if settings.llm_provider == "openai":
        provider = OpenAIProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
    else:
        provider = MockLLMProvider(
            {
                "account": {
                    "holder_name": "Test Employee",
                    "bank_name": "Example Bank",
                    "account_number": "XXXXXX1234",
                    "ifsc": "EXMP0001234",
                },
                "statement_period": {
                    "from_date": "2026-08-01",
                    "to_date": "2026-08-31",
                },
                "opening_balance": "100000",
                "closing_balance": "131000",
                "transactions": [
                    {
                        "date": "2026-08-01",
                        "narration": "SALARY CREDIT AUGUST 2026",
                        "debit": None,
                        "credit": "59000",
                        "balance": "159000",
                    },
                    {
                        "date": "2026-08-05",
                        "narration": "HOME LOAN EMI",
                        "debit": "18000",
                        "credit": None,
                        "balance": "141000",
                    },
                    {
                        "date": "2026-08-10",
                        "narration": "UTILITY PAYMENT",
                        "debit": "5000",
                        "credit": None,
                        "balance": "136000",
                    },
                    {
                        "date": "2026-08-15",
                        "narration": "TRANSFER FROM SAVINGS",
                        "debit": None,
                        "credit": "25000",
                        "balance": "161000",
                    },
                    {
                        "date": "2026-08-20",
                        "narration": "ONLINE PURCHASE",
                        "debit": "30000",
                        "credit": None,
                        "balance": "131000",
                    },
                ],
            }
        )

    return LlmBankExtractor(provider)