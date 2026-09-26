import json
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

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
10. Dates MUST use ISO format YYYY-MM-DD.
11. Monetary values MUST be plain decimal strings without currency symbols,
    commas, or other thousands separators.
12. Examples:
    - "01 Jul 2025" -> "2025-07-01"
    - "31 Aug 2025" -> "2025-08-31"
    - "1,20,000.00" -> "120000.00"
    - "₹50,000" -> "50000"
13. Return only structured JSON matching the requested schema.
""".strip()

    USER_PROMPT_TEMPLATE = """
Extract the following bank statement into the required structured schema.

Important formatting requirements:

- All dates must be YYYY-MM-DD.
- All monetary values must be plain decimal strings without commas,
  currency symbols, or thousands separators.
- Do not calculate or modify financial values.
- Preserve the values exactly apart from formatting normalization.

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

            normalized_response = self._normalize_response(response)

            return BankStatement.model_validate(normalized_response)

        except (ValidationError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise BankExtractionError(
                "LLM returned invalid bank statement data."
            ) from exc

    @classmethod
    def _normalize_response(cls, response: dict) -> dict:
        """
        Normalize common LLM representations before Pydantic validation.

        The LLM is allowed to return human-readable financial formatting,
        while the domain model receives canonical date/Decimal-compatible
        values.
        """
        normalized = dict(response)

        statement_period = normalized.get("statement_period")
        if isinstance(statement_period, dict):
            normalized["statement_period"] = {
                **statement_period,
                "from_date": cls._normalize_date(
                    statement_period.get("from_date")
                ),
                "to_date": cls._normalize_date(
                    statement_period.get("to_date")
                ),
            }

        normalized["opening_balance"] = cls._normalize_decimal(
            normalized.get("opening_balance")
        )
        normalized["closing_balance"] = cls._normalize_decimal(
            normalized.get("closing_balance")
        )

        transactions = normalized.get("transactions")

        if isinstance(transactions, list):
            normalized["transactions"] = [
                cls._normalize_transaction(transaction)
                for transaction in transactions
            ]

        return normalized

    @classmethod
    def _normalize_transaction(cls, transaction: object) -> object:
        if not isinstance(transaction, dict):
            return transaction

        return {
            **transaction,
            "date": cls._normalize_date(transaction.get("date")),
            "debit": cls._normalize_decimal(transaction.get("debit")),
            "credit": cls._normalize_decimal(transaction.get("credit")),
            "balance": cls._normalize_decimal(transaction.get("balance")),
        }

    @staticmethod
    def _normalize_date(value: object) -> object:
        """
        Convert common date representations to ISO YYYY-MM-DD.

        Pydantic ultimately validates the returned value as a date.
        Unknown values are left untouched so validation can report them.
        """
        if value is None or isinstance(value, date):
            return value

        if isinstance(value, datetime):
            return value.date().isoformat()

        if not isinstance(value, str):
            return value

        value = value.strip()

        if not value:
            return None

        # Already ISO formatted.
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError:
            pass

        date_formats = (
            "%d %b %Y",
            "%d %B %Y",
            "%d-%b-%Y",
            "%d-%B-%Y",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d/%m/%y",
            "%d-%m-%y",
        )

        for date_format in date_formats:
            try:
                return datetime.strptime(value, date_format).date().isoformat()
            except ValueError:
                continue

        return value

    @staticmethod
    def _normalize_decimal(value: object) -> object:
        """
        Normalize human-formatted monetary values.

        Examples:
            "1,20,000.00" -> "120000.00"
            "₹50,000"     -> "50000"
            " 12,500.00 " -> "12500.00"
        """
        if value is None or isinstance(value, Decimal):
            return value

        if isinstance(value, (int, float)):
            return str(value)

        if not isinstance(value, str):
            return value

        cleaned = value.strip()

        if not cleaned:
            return None

        # Remove common currency symbols and whitespace.
        cleaned = cleaned.replace("₹", "")
        cleaned = cleaned.replace("Rs.", "")
        cleaned = cleaned.replace("Rs", "")
        cleaned = cleaned.replace("INR", "")
        cleaned = re.sub(r"\s+", "", cleaned)

        # Remove thousands separators, including Indian lakh/crore grouping.
        cleaned = cleaned.replace(",", "")

        # Keep the canonical numeric value if possible.
        try:
            decimal_value = Decimal(cleaned)
        except InvalidOperation:
            return value

        return format(decimal_value, "f")