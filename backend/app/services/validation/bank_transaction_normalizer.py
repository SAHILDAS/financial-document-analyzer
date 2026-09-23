import re
from decimal import Decimal, InvalidOperation

from app.schemas.bank_statement import BankTransaction


class BankTransactionNormalizer:
    """Normalize extracted bank transaction values."""

    CURRENCY_PREFIX_PATTERN = re.compile(r"^[₹$€£]\s*")

    @classmethod
    def normalize_narration(cls, narration: str) -> str:
        """Normalize whitespace in transaction narration."""

        return " ".join(narration.split()).strip()

    @classmethod
    def normalize_amount(
        cls,
        value: Decimal | str | int | float | None,
    ) -> Decimal | None:
        """Normalize a monetary value into Decimal."""

        if value is None:
            return None

        if isinstance(value, Decimal):
            return value

        text = str(value).strip()

        if not text:
            return None

        text = cls.CURRENCY_PREFIX_PATTERN.sub("", text)
        text = text.replace(",", "")
        text = text.strip()

        try:
            return Decimal(text)
        except InvalidOperation as exc:
            raise ValueError(
                f"Invalid monetary value: {value}"
            ) from exc

    @classmethod
    def normalize(cls, transaction: BankTransaction) -> BankTransaction:
        """Return a normalized copy of a bank transaction."""

        return transaction.model_copy(
            update={
                "narration": cls.normalize_narration(transaction.narration),
                "debit": cls.normalize_amount(transaction.debit),
                "credit": cls.normalize_amount(transaction.credit),
                "balance": cls.normalize_amount(transaction.balance),
            }
        )