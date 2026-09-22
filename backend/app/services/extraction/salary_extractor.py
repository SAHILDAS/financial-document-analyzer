from abc import abstractmethod

from app.schemas.salary_slip import SalarySlip
from app.services.extraction.base import ExtractionService


class SalaryExtractionError(Exception):
    """Raised when salary extraction cannot produce valid structured data."""


class SalaryExtractionService(ExtractionService[SalarySlip]):
    """Contract for extracting structured salary-slip data."""

    @abstractmethod
    def extract(self, text: str) -> SalarySlip:
        """Extract salary information from document text."""
        raise NotImplementedError