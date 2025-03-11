"""
LLM Client module.
Wraps calls to the LLM (e.g., GPT-4) using the OpenAI API.
"""

import openai
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LLMClient:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key

    def call_llm(self, prompt, model="gpt-4", temperature=0.7, max_tokens=512):
        """
        Calls the LLM with the given prompt and returns the response text.
        """
        logger.debug("LLMClient: Calling LLM with prompt: %s", prompt[:100])
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "system", "content": "You are an OSINT assistant."},
                          {"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                n=1,
                stop=None,
            )
            text = response.choices[0].message['content']
            return text.strip()
        except Exception as e:
            logger.error("LLM call failed: %s", str(e))
            return "LLM Error: Unable to process the request."