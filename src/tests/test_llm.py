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
        providers = ["openai", "anthropic", "mistral", "kilocode"]
        for provider in providers:
            with self.subTest(provider=provider):
                llm_client = LLMClient(rate_limit=0)
                failing_mock = MagicMock(side_effect=Exception(f"{provider} failure"))
                llm_client._providers = [(provider, failing_mock)]
                response = llm_client.call_llm("Test prompt")
                self.assertIn("LLM Error", response)
                self.assertIn(f"{provider} failure", response)
                failing_mock.assert_called_once()

    def test_call_llm_all_providers_fail_returns_error(self) -> None:
        openai_mock = MagicMock(side_effect=Exception("OpenAI failure"))
        anthropic_mock = MagicMock(side_effect=Exception("Anthropic failure"))
        mistral_mock = MagicMock(side_effect=Exception("Mistral failure"))
        kilocode_mock = MagicMock(side_effect=Exception("Kilocode failure"))
        self.llm_client._providers = [
            ("openai", openai_mock),
            ("anthropic", anthropic_mock),
            ("mistral", mistral_mock),
            ("kilocode", kilocode_mock),
        ]
        response = self.llm_client.call_llm("Test prompt")
        self.assertIn("LLM Error", response)
        self.assertIn("OpenAI failure", response)
        self.assertIn("Anthropic failure", response)
        self.assertIn("Mistral failure", response)
        self.assertIn("Kilocode failure", response)
        openai_mock.assert_called_once()
        anthropic_mock.assert_called_once()
        mistral_mock.assert_called_once()
        kilocode_mock.assert_called_once()

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
        kilocode_mock = MagicMock(return_value="Kilocode response")
        self.llm_client._providers = [
            ("openai", openai_mock),
            ("anthropic", anthropic_mock),
            ("mistral", mistral_mock),
            ("kilocode", kilocode_mock),
        ]
        response = self.llm_client.call_llm("Test prompt")
        self.assertEqual(response, "Mistral response")
        openai_mock.assert_called_once()
        anthropic_mock.assert_called_once()
        mistral_mock.assert_called_once()
        kilocode_mock.assert_not_called()

    def test_fallback_to_kilocode_when_others_fail(self) -> None:
        openai_mock = MagicMock(side_effect=Exception("OpenAI failure"))
        anthropic_mock = MagicMock(side_effect=Exception("Anthropic failure"))
        mistral_mock = MagicMock(side_effect=Exception("Mistral failure"))
        kilocode_mock = MagicMock(return_value="Kilocode response")
        self.llm_client._providers = [
            ("openai", openai_mock),
            ("anthropic", anthropic_mock),
            ("mistral", mistral_mock),
            ("kilocode", kilocode_mock),
        ]
        response = self.llm_client.call_llm("Test prompt")
        self.assertEqual(response, "Kilocode response")
        openai_mock.assert_called_once()
        anthropic_mock.assert_called_once()
        mistral_mock.assert_called_once()
        kilocode_mock.assert_called_once()

    def test_no_providers_returns_error_message(self) -> None:
        self.llm_client._providers = []
        response = self.llm_client.call_llm("Test prompt")
        self.assertEqual(response, "LLM Error: No providers are configured.")

    def test_custom_provider_order_is_respected(self) -> None:
        anthropic_mock = MagicMock(return_value="Anthropic response")
        openai_mock = MagicMock(return_value="OpenAI response")
        self.llm_client.anthropic_client = object()
        self.llm_client.openai_client = object()
        self.llm_client._call_anthropic = anthropic_mock  # type: ignore[attr-defined]
        self.llm_client._call_openai = openai_mock  # type: ignore[attr-defined]
        self.llm_client._providers = self.llm_client._build_provider_registry(
            ["anthropic", "openai"]
        )
        response = self.llm_client.call_llm("Test prompt")
        self.assertEqual(response, "Anthropic response")
        anthropic_mock.assert_called_once()
        openai_mock.assert_not_called()

    def test_model_overrides_are_applied(self) -> None:
        provider_mock = MagicMock(return_value="Summary")
        self.llm_client.openai_client = object()
        self.llm_client._call_openai = provider_mock  # type: ignore[attr-defined]
        self.llm_client._providers = self.llm_client._build_provider_registry(["openai"])
        response = self.llm_client.call_llm(
            "Prompt", model_overrides={"openai": "gpt-custom"}
        )
        self.assertEqual(response, "Summary")
        provider_mock.assert_called_once()
        _, model_arg, _, _ = provider_mock.call_args[0]
        self.assertEqual(model_arg, "gpt-custom")


if __name__ == "__main__":
    unittest.main()
