from typing import Any

from app.services.extraction.providers.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """
    Deterministic LLM provider used for local development and tests.

    No external network request is made.
    """

    def __init__(self, response: dict[str, Any]):
        self.response = response

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        return self.response.copy()