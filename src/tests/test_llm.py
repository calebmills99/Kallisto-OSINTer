"""Unit tests for the LLM module."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from src.llm.llm_client import LLMClient


class TestLLMClient(unittest.TestCase):
    def setUp(self) -> None:
        self.llm_client = LLMClient(rate_limit=0)

    def test_call_llm_returns_string(self) -> None:
        prompt = "Summarize the following text: Hello world."
        provider_mock = MagicMock(return_value="summary")
        self.llm_client._providers = [("openai", provider_mock)]
        response = self.llm_client.call_llm(prompt)
        self.assertEqual(response, "summary")
        provider_mock.assert_called_once()

    def test_call_llm_error_handling(self) -> None:
        providers = ["openai", "anthropic", "mistral"]
        for provider in providers:
            with self.subTest(provider=provider):
                llm_client = LLMClient(rate_limit=0)
                failing_mock = MagicMock(side_effect=Exception(f"{provider} failure"))
                llm_client._providers = [(provider, failing_mock)]
                response = llm_client.call_llm("Test prompt")
                self.assertIn("LLM Error", response)
                failing_mock.assert_called_once()

    def test_call_llm_all_providers_fail_returns_error(self) -> None:
        openai_mock = MagicMock(side_effect=Exception("OpenAI failure"))
        anthropic_mock = MagicMock(side_effect=Exception("Anthropic failure"))
        mistral_mock = MagicMock(side_effect=Exception("Mistral failure"))
        self.llm_client._providers = [
            ("openai", openai_mock),
            ("anthropic", anthropic_mock),
            ("mistral", mistral_mock),
        ]
        response = self.llm_client.call_llm("Test prompt")
        self.assertIn("LLM Error", response)
        openai_mock.assert_called_once()
        anthropic_mock.assert_called_once()
        mistral_mock.assert_called_once()

    def test_fallback_to_anthropic_when_openai_fails(self) -> None:
        openai_mock = MagicMock(side_effect=Exception("OpenAI failure"))
        anthropic_mock = MagicMock(return_value="Anthropic response")
        mistral_mock = MagicMock(return_value="Mistral response")
        self.llm_client._providers = [
            ("openai", openai_mock),
            ("anthropic", anthropic_mock),
            ("mistral", mistral_mock),
        ]
        response = self.llm_client.call_llm("Test prompt")
        self.assertEqual(response, "Anthropic response")
        openai_mock.assert_called_once()
        anthropic_mock.assert_called_once()
        mistral_mock.assert_not_called()

    def test_fallback_to_mistral_when_openai_and_anthropic_fail(self) -> None:
        openai_mock = MagicMock(side_effect=Exception("OpenAI failure"))
        anthropic_mock = MagicMock(side_effect=Exception("Anthropic failure"))
        mistral_mock = MagicMock(return_value="Mistral response")
        self.llm_client._providers = [
            ("openai", openai_mock),
            ("anthropic", anthropic_mock),
            ("mistral", mistral_mock),
        ]
        response = self.llm_client.call_llm("Test prompt")
        self.assertEqual(response, "Mistral response")
        openai_mock.assert_called_once()
        anthropic_mock.assert_called_once()
        mistral_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
