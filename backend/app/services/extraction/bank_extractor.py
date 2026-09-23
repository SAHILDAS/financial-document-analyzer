from abc import ABC, abstractmethod

from app.schemas.bank_statement import BankStatement


class BankExtractionError(Exception):
    """Raised when bank statement extraction fails."""


class BankExtractionService(ABC):
    """Contract for extracting structured bank statements."""

    @abstractmethod
    def extract(self, text: str) -> BankStatement:
        """Extract a structured bank statement from document text."""
        raise NotImplementedError