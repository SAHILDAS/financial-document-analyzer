from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class ExtractionService(ABC, Generic[T]):
    """Base contract for structured document extraction."""

    @abstractmethod
    def extract(self, text: str) -> T:
        """Extract structured data from document text."""
        raise NotImplementedError