from unittest.mock import Mock

import pytest

from app.services.extraction.providers.openai_provider import (
    LLMProviderError,
    OpenAIProvider,
)


def test_prepare_strict_schema_marks_object_properties_required():
    schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": ["string", "null"],
            },
            "amount": {
                "type": ["string", "null"],
            },
        },
    }

    prepared = OpenAIProvider._prepare_strict_schema(schema)

    assert prepared["required"] == [
        "name",
        "amount",
    ]

    assert prepared["additionalProperties"] is False


def test_prepare_strict_schema_handles_nested_objects():
    schema = {
        "type": "object",
        "properties": {
            "account": {
                "type": "object",
                "properties": {
                    "holder_name": {
                        "type": ["string", "null"],
                    },
                },
            },
        },
    }

    prepared = OpenAIProvider._prepare_strict_schema(schema)

    account_schema = prepared["properties"]["account"]

    assert account_schema["required"] == [
        "holder_name",
    ]

    assert account_schema["additionalProperties"] is False


def test_generate_structured_returns_dictionary():
    provider = OpenAIProvider(
        api_key="test-key",
        model="gpt-5.6-luna",
    )

    fake_response = Mock()
    fake_response.output_text = (
        '{"name": "Test Employee", "amount": "59000"}'
    )

    fake_client = Mock()
    fake_client.responses.create.return_value = fake_response

    provider._client = fake_client

    result = provider.generate_structured(
        system_prompt="Extract data.",
        user_prompt="Name: Test Employee Amount: 59000",
        response_schema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                },
                "amount": {
                    "type": "string",
                },
            },
        },
    )

    assert result == {
        "name": "Test Employee",
        "amount": "59000",
    }

    fake_client.responses.create.assert_called_once()


def test_generate_structured_rejects_empty_user_prompt():
    provider = OpenAIProvider(
        api_key="test-key",
        model="gpt-5.6-luna",
    )

    with pytest.raises(LLMProviderError):
        provider.generate_structured(
            system_prompt="Extract data.",
            user_prompt="   ",
            response_schema={
                "type": "object",
                "properties": {},
            },
        )