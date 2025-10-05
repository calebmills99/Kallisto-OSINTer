"""
LLM Client module.
Wraps calls to the LLM (e.g., GPT-4) using the OpenAI API with rate limiting.
"""

import time
from openai import OpenAI
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Global rate limiting for LLM calls
_last_llm_call_time = 0
_min_llm_call_interval = 2.0  # minimum seconds between LLM calls

class LLMClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    def call_llm(self, prompt, model="gpt-4", temperature=0.7, max_tokens=512):
        """
        Calls the LLM with the given prompt and returns the response text.
        Includes rate limiting to avoid API throttling.
        """
        global _last_llm_call_time

        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - _last_llm_call_time
        if time_since_last < _min_llm_call_interval:
            sleep_time = _min_llm_call_interval - time_since_last
            logger.debug("LLM rate limiting: sleeping for %.2f seconds", sleep_time)
            time.sleep(sleep_time)

        logger.debug("LLMClient: Calling LLM with prompt: %s", prompt[:100])
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": "You are an OSINT assistant."},
                          {"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                n=1,
                stop=None,
            )
            _last_llm_call_time = time.time()
            text = response.choices[0].message.content
            return text.strip()
        except Exception as e:
            logger.error("LLM call failed: %s", str(e))
            _last_llm_call_time = time.time()  # Update time even on error
            return "LLM Error: Unable to process the request."