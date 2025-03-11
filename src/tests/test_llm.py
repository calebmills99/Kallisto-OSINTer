"""
Unit tests for the LLM module.
Uses Python's built-in unittest framework.
"""

import unittest
from src.llm.llm_client import LLMClient

class TestLLMClient(unittest.TestCase):
    def setUp(self):
        # Use a dummy API key for testing; in practice, you might mock openai.
        self.llm_client = LLMClient(api_key="dummy_key")

    def test_call_llm_returns_string(self):
        prompt = "Summarize the following text: Hello world."
        # Here we simulate a call by overriding the function if needed.
        response = self.llm_client.call_llm(prompt)
        self.assertIsInstance(response, str)

    def test_call_llm_error_handling(self):
        # Intentionally pass a prompt that causes an error (simulate by passing empty API key)
        self.llm_client.api_key = ""
        response = self.llm_client.call_llm("Test prompt")
        self.assertTrue("LLM Error" in response)

if __name__ == "__main__":
    unittest.main()