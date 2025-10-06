"""Unit tests for the LLM module."""

from __future__ import annotations

import unittest

from src.llm.llm_client import LLMClient


class TestLLMClient(unittest.TestCase):
    def setUp(self) -> None:
        self.llm_client = LLMClient()

    def test_call_llm_returns_string(self) -> None:
        prompt = "Summarize the following text: Hello world."
        response = self.llm_client.call_llm(prompt)
        self.assertIsInstance(response, str)

    def test_call_llm_error_handling(self) -> None:
        response = self.llm_client.call_llm("Test prompt")
        self.assertIn("LLM Error", response)


if __name__ == "__main__":
    unittest.main()
