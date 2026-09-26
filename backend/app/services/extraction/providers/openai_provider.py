import json
from copy import deepcopy
from typing import Any

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    OpenAI,
)

from app.core.config import settings
from app.services.extraction.providers.base import LLMProvider


class LLMProviderError(RuntimeError):
    """Provider-level failure during structured LLM generation."""


class OpenAIProvider(LLMProvider):
    """
    OpenAI implementation of the provider-agnostic LLM contract.

    The application sends document text to OpenAI and requests a
    strict JSON-schema-constrained response.

    The provider returns a plain Python dictionary so the existing
    extraction services remain provider-independent.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.llm_model
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        """Create the OpenAI client lazily."""
        if self._client is None:
            if not self.api_key:
                raise LLMProviderError(
                    "OpenAI API key is not configured."
                )

            self._client = OpenAI(
                api_key=self.api_key,
                timeout=self.timeout,
                max_retries=self.max_retries,
            )

        return self._client

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate structured JSON using OpenAI Responses API.

        The response schema is normalized for strict structured output,
        then the returned JSON is converted into a Python dictionary.
        """

        if not system_prompt.strip():
            raise LLMProviderError(
                "System prompt cannot be empty."
            )

        if not user_prompt.strip():
            raise LLMProviderError(
                "User prompt cannot be empty."
            )

        if not response_schema:
            raise LLMProviderError(
                "Response schema cannot be empty."
            )

        schema = self._prepare_strict_schema(response_schema)

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "financial_document_extraction",
                        "strict": True,
                        "schema": schema,
                    }
                },
            )

        except APITimeoutError as exc:
            raise LLMProviderError(
                "OpenAI request timed out."
            ) from exc

        except APIConnectionError as exc:
            raise LLMProviderError(
                "Unable to connect to the OpenAI API."
            ) from exc

        except APIError as exc:
            raise LLMProviderError(
                "OpenAI API request failed."
            ) from exc

        except Exception as exc:
            raise LLMProviderError(
                "Unexpected OpenAI provider failure."
            ) from exc

        output_text = getattr(response, "output_text", None)

        if not output_text or not output_text.strip():
            raise LLMProviderError(
                "OpenAI returned an empty structured response."
            )

        try:
            parsed = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise LLMProviderError(
                "OpenAI returned invalid JSON."
            ) from exc

        if not isinstance(parsed, dict):
            raise LLMProviderError(
                "OpenAI structured response must be a JSON object."
            )

        return parsed

    @classmethod
    def _prepare_strict_schema(
        cls,
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert the application schema into a strict JSON Schema.

        OpenAI Structured Outputs requires object properties to be
        explicitly required and disallows additional properties in
        strict object schemas.

        Nullable fields remain nullable through their existing schema.
        """

        schema = deepcopy(response_schema)

        cls._normalize_schema_node(schema)

        return schema

    @classmethod
    def _normalize_schema_node(
        cls,
        node: Any,
    ) -> None:
        """Recursively normalize JSON Schema nodes."""

        if isinstance(node, dict):
            # Pydantic may generate regex patterns for Decimal and
            # constrained string schemas. Some patterns contain
            # regex lookaround that is not accepted by OpenAI
            # Structured Outputs.
            #
            # Pattern-level validation remains enforced by the
            # application's Pydantic model after LLM generation.
            node.pop("$schema", None)
            node.pop("pattern", None)

            if node.get("type") == "object":
                properties = node.get("properties")

                if isinstance(properties, dict):
                    node["required"] = list(properties.keys())
                    node["additionalProperties"] = False

                    for property_schema in properties.values():
                        cls._normalize_schema_node(property_schema)

                additional_properties = node.get(
                    "additionalProperties"
                )

                if isinstance(additional_properties, dict):
                    cls._normalize_schema_node(
                        additional_properties
                    )

            if node.get("type") == "array":
                items = node.get("items")

                if isinstance(items, dict):
                    cls._normalize_schema_node(items)

            for key in (
                "anyOf",
                "oneOf",
                "allOf",
            ):
                variants = node.get(key)

                if isinstance(variants, list):
                    for variant in variants:
                        cls._normalize_schema_node(variant)

            definitions = node.get("$defs")

            if isinstance(definitions, dict):
                for definition in definitions.values():
                    cls._normalize_schema_node(definition)

            definitions = node.get("definitions")

            if isinstance(definitions, dict):
                for definition in definitions.values():
                    cls._normalize_schema_node(definition)

        elif isinstance(node, list):
            for item in node:
                cls._normalize_schema_node(item)