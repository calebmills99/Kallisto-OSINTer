"""
Unit tests for LangChain Integration module.
"""

import unittest
from src.langchain_integration import LangChainIntegrator, run_langchain_pipeline, debug_langchain_integrator

class TestLangChainIntegration(unittest.TestCase):
    def setUp(self):
        self.integrator = LangChainIntegrator(api_key="dummy_key")

    def test_build_chain(self):
        prompt_template = "Summarize: {input}"
        chain = self.integrator.build_chain(prompt_template)
        self.assertIsNotNone(chain)

    def test_run_chain_error(self):
        # Since dummy API key, expect error in run_chain (or a fallback error string)
        prompt_template = "Summarize: {input}"
        self.integrator.build_chain(prompt_template)
        result = self.integrator.run_chain("Test input")
        self.assertIsInstance(result, str)

    def test_run_langchain_pipeline(self):
        result = run_langchain_pipeline("Dummy OSINT data")
        self.assertIsInstance(result, str)

    def test_debug_function(self):
        result = debug_langchain_integrator()
        self.assertIsInstance(result, str)

if __name__ == "__main__":
    unittest.main()