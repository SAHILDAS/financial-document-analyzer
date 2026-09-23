import json

from pydantic import ValidationError

from app.schemas.bank_statement import BankStatement
from app.services.extraction.bank_extractor import (
    BankExtractionError,
    BankExtractionService,
)
from app.services.extraction.providers.base import LLMProvider


class LlmBankExtractor(BankExtractionService):
    """Extract a structured bank statement using an LLM provider."""

    SYSTEM_PROMPT = """
You are a financial document extraction system.

Extract structured information from bank statements.

Rules:

1. Extract only information explicitly present in the document.
2. Never invent missing values.
3. Use null when a field is unavailable.
4. Preserve transaction narration as accurately as possible.
5. Do not calculate balances, totals, or derived financial values.
6. Do not infer that a transaction is salary, EMI, loan, or recurring.
7. Preserve debit and credit amounts separately.
8. Preserve the transaction date.
9. Preserve the running balance when available.
10. Return only structured JSON matching the requested schema.
""".strip()

    USER_PROMPT_TEMPLATE = """
Extract the following bank statement into the required structured schema.

Document text:

{text}
""".strip()

    RESPONSE_SCHEMA = {
        "type": "object",
        "properties": {
            "account": {
                "type": "object",
                "properties": {
                    "holder_name": {"type": ["string", "null"]},
                    "bank_name": {"type": ["string", "null"]},
                    "account_number": {"type": ["string", "null"]},
                    "ifsc": {"type": ["string", "null"]},
                },
            },
            "statement_period": {
                "type": "object",
                "properties": {
                    "from_date": {"type": ["string", "null"]},
                    "to_date": {"type": ["string", "null"]},
                },
            },
            "opening_balance": {
                "type": ["string", "null"],
            },
            "closing_balance": {
                "type": ["string", "null"],
            },
            "transactions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string"},
                        "narration": {"type": "string"},
                        "debit": {"type": ["string", "null"]},
                        "credit": {"type": ["string", "null"]},
                        "balance": {"type": ["string", "null"]},
                    },
                    "required": [
                        "date",
                        "narration",
                        "debit",
                        "credit",
                        "balance",
                    ],
                },
            },
        },
        "required": [
            "account",
            "statement_period",
            "opening_balance",
            "closing_balance",
            "transactions",
        ],
    }

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def extract(self, text: str) -> BankStatement:
        if not text or not text.strip():
            raise BankExtractionError(
                "Cannot extract a bank statement from empty text."
            )

        prompt = self.USER_PROMPT_TEMPLATE.format(text=text)

        try:
            response = self.provider.generate_structured(
                system_prompt=self.SYSTEM_PROMPT,
                user_prompt=prompt,
                response_schema=self.RESPONSE_SCHEMA,
            )
        except Exception as exc:
            raise BankExtractionError(
                "Structured bank statement extraction failed."
            ) from exc

        try:
            if isinstance(response, str):
                response = json.loads(response)

            if not isinstance(response, dict):
                raise TypeError(
                    "Provider returned an unsupported response."
                )

            return BankStatement.model_validate(response)

        except (ValidationError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise BankExtractionError(
                "LLM returned invalid bank statement data."
            ) from exc