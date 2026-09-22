from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Provider-agnostic contract for structured LLM generation."""

    @abstractmethod
    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate structured data from an LLM.

        Implementations are responsible for communicating with the
        underlying provider and returning JSON-compatible data.
        """
        raise NotImplementedError