from pydantic import ValidationError

from app.schemas.salary_slip import SalarySlip
from app.services.extraction.providers.base import LLMProvider
from app.services.extraction.salary_extractor import (
    SalaryExtractionError,
    SalaryExtractionService,
)


class LlmSalaryExtractor(SalaryExtractionService):
    """Extract salary-slip data using a structured LLM provider."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def extract(self, text: str) -> SalarySlip:
        """
        Extract a structured SalarySlip from document text.

        Provider failures and invalid provider responses are converted
        into SalaryExtractionError so callers do not depend on
        provider-specific exceptions.
        """
        if not text.strip():
            raise SalaryExtractionError(
                "Salary document text cannot be empty."
            )

        try:
            response = self.provider.generate_structured(
                system_prompt=self._build_system_prompt(),
                user_prompt=text,
                response_schema=self._response_schema(),
            )
        except Exception as exc:
            raise SalaryExtractionError(
                "The salary extraction provider failed."
            ) from exc

        try:
            return SalarySlip.model_validate(response)
        except ValidationError as exc:
            raise SalaryExtractionError(
                "The extraction provider returned invalid salary data."
            ) from exc

    @staticmethod
    def _build_system_prompt() -> str:
        return """
You are a financial document extraction engine.

Your task is to extract structured salary-slip information from
the supplied document text.

GENERAL RULES
-------------
1. Extract only information explicitly supported by the document.
2. Never invent, guess, infer, or fabricate a value.
3. Use null when a field is missing, unreadable, or not explicitly stated.
4. Preserve the meaning of the source document.
5. Do not perform financial validation.
6. Do not calculate missing monetary values.
7. Do not assume that a missing amount is zero.
8. Return only data matching the supplied JSON schema.

EMPLOYEE INFORMATION
--------------------
Extract:
- employee name
- employee ID
- employer name
- salary month/pay period
- PAN, if explicitly present

SALARY EARNINGS
---------------
Extract:
- basic salary/basic pay
- HRA/house rent allowance
- allowances
- bonus
- incentives
- other earnings
- gross salary

If multiple allowance categories are present and the schema has
only one allowances field, combine only explicitly stated allowance
amounts into that field.

SALARY DEDUCTIONS
-----------------
Extract:
- provident fund/PF
- professional tax
- TDS
- other deductions
- total deductions

Do not calculate total deductions if the document does not explicitly
provide a total.

NET SALARY
----------
Extract the explicitly stated net salary/net pay/take-home salary.

Do not calculate net salary from gross salary minus deductions.

BANK ACCOUNT
------------
Extract the salary bank account number only if explicitly present.

PII HANDLING
------------
Preserve extracted PII only in the structured response required by
the application. Do not add unrelated personal information.

MONETARY VALUES
---------------
Return monetary values as numbers compatible with the supplied schema.
Do not include currency symbols inside numeric values.

MISSING VALUES
--------------
Missing is not the same as zero.

For example:
- no bonus shown -> bonus = null
- bonus explicitly shown as 0 -> bonus = 0
- professional tax not present -> professional_tax = null

OUTPUT
------
Return only structured JSON conforming to the supplied response schema.
""".strip()

    @staticmethod
    def _response_schema() -> dict:
        schema = SalarySlip.model_json_schema()

        schema["description"] = (
            "Structured representation of a salary slip. "
            "Missing values must be null and must not be inferred."
        )

        return schema