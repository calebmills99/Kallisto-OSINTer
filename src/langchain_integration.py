"""
LangChain Integration module.
This module integrates LangChain to create chains that process OSINT results.
Provides classes to build, run, and visualize LangChain pipelines.
"""

from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from src.config import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LangChainIntegrator:
    def __init__(self, api_key=None):
        config = load_config()
        self.api_key = api_key if api_key else config.get('OPENAI_API_KEY', '')
        self.llm = OpenAI(api_key=self.api_key, model_name="gpt-4", temperature=0.7)
        self.chain = None

    def build_chain(self, prompt_template, output_key="output"):
        """
        Builds a LangChain LLMChain with the provided prompt template.
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["input"])
        self.chain = LLMChain(llm=self.llm, prompt=prompt, output_key=output_key)
        logger.info("LangChain chain built with template: %s", prompt_template)
        return self.chain

    def run_chain(self, input_text):
        """
        Runs the chain with the provided input text.
        """
        if not self.chain:
            raise ValueError("Chain is not built. Call build_chain first.")
        logger.info("Running LangChain chain with input: %s", input_text[:100])
        result = self.chain.run(input=input_text)
        return result

    def advanced_chain(self, osint_data):
        """
        Builds and runs an advanced chain that processes OSINT data.
        For example, this chain might analyze, summarize, and generate insights.
        """
        advanced_template = (
            "You are an OSINT expert. Analyze the following data, summarize key findings, and provide actionable insights:\n\n"
            "{input}\n\nSummary and Insights:"
        )
        self.build_chain(advanced_template)
        result = self.run_chain(osint_data)
        return result

    def build_custom_chain(self, prompt_template, input_vars):
        """
        Builds a custom chain with dynamic input variables.
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=input_vars)
        custom_chain = LLMChain(llm=self.llm, prompt=prompt)
        logger.info("Custom LangChain chain built with variables: %s", input_vars)
        return custom_chain

    def run_custom_chain(self, custom_chain, input_dict):
        """
        Runs a provided custom chain with a dictionary of inputs.
        """
        logger.info("Running custom chain with inputs: %s", input_dict)
        result = custom_chain.run(input_dict)
        return result

# Additional helper functions for LangChain integration.
def run_langchain_pipeline(osint_data):
    """
    Convenience function to run a full LangChain pipeline on OSINT data.
    """
    integrator = LangChainIntegrator()
    result = integrator.advanced_chain(osint_data)
    return result

def debug_langchain_integrator():
    """
    Runs a sample LangChain pipeline for debugging purposes.
    """
    sample_data = "Test OSINT data: A person with notable online presence in cybersecurity."
    integrator = LangChainIntegrator()
    chain = integrator.build_chain("Summarize the following OSINT data:\n\n{input}\n\nSummary:")
    result = integrator.run_chain(sample_data)
    logger.debug("Debug LangChain result: %s", result)
    return result