"""LLM Client module.

Wraps calls to available large language model providers with rate limiting and
fallback behaviour. The client will attempt to use OpenAI first, then Anthropic
and finally Mistral if earlier providers fail.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from src.utils.logger import get_logger

try:  # pragma: no cover - optional dependency
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled gracefully
    OpenAI = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from anthropic import Anthropic
except ImportError:  # pragma: no cover - handled gracefully
    Anthropic = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
except ImportError:  # pragma: no cover - handled gracefully
    MistralClient = None  # type: ignore
    ChatMessage = None  # type: ignore

logger = get_logger(__name__)

_DEFAULT_SYSTEM_PROMPT = "You are an OSINT assistant."

_last_llm_call_time = 0.0


class LLMClient:
    """Wrapper around multiple LLM providers with fallback support."""

    def __init__(
        self,
        openai_key: Optional[str] = None,
        anthropic_key: Optional[str] = None,
        mistral_key: Optional[str] = None,
        rate_limit: float = 2.0,
        system_prompt: str = _DEFAULT_SYSTEM_PROMPT,
    ) -> None:
        self.rate_limit = max(rate_limit, 0.0)
        self.system_prompt = system_prompt

        self.openai_key = openai_key or ""
        self.anthropic_key = anthropic_key or ""
        self.mistral_key = mistral_key or ""

        self.openai_client = self._build_openai_client()
        self.anthropic_client = self._build_anthropic_client()
        self.mistral_client = self._build_mistral_client()

        self._provider_order: List[str] = []
        if self.openai_client is not None:
            self._provider_order.append("openai")
        if self.anthropic_client is not None:
            self._provider_order.append("anthropic")
        if self.mistral_client is not None:
            self._provider_order.append("mistral")

        if not self._provider_order:
            logger.warning("LLMClient initialized without any available providers.")

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "LLMClient":
        """Instantiate the client using a configuration dictionary."""

        return cls(
            openai_key=config.get("OPENAI_API_KEY"),
            anthropic_key=config.get("ANTHROPIC_API_KEY"),
            mistral_key=config.get("MISTRAL_API_KEY"),
            rate_limit=float(config.get("LLM_RATE_LIMIT", 2.0)),
        )

    def _build_openai_client(self) -> Optional[OpenAI]:
        if not self.openai_key or OpenAI is None:
            return None
        try:
            return OpenAI(api_key=self.openai_key)
        except Exception as exc:  # pragma: no cover - network failures
            logger.error("Failed to initialize OpenAI client: %s", exc)
            return None

    def _build_anthropic_client(self) -> Optional[Anthropic]:
        if not self.anthropic_key or Anthropic is None:
            return None
        try:
            return Anthropic(api_key=self.anthropic_key)
        except Exception as exc:  # pragma: no cover - network failures
            logger.error("Failed to initialize Anthropic client: %s", exc)
            return None

    def _build_mistral_client(self) -> Optional[MistralClient]:
        if not self.mistral_key or MistralClient is None:
            return None
        try:
            return MistralClient(api_key=self.mistral_key)
        except Exception as exc:  # pragma: no cover - network failures
            logger.error("Failed to initialize Mistral client: %s", exc)
            return None

    def _respect_rate_limit(self) -> None:
        global _last_llm_call_time
        if self.rate_limit <= 0:
            return
        current_time = time.time()
        elapsed = current_time - _last_llm_call_time
        if elapsed < self.rate_limit:
            sleep_time = self.rate_limit - elapsed
            logger.debug("LLM rate limiting: sleeping for %.2f seconds", sleep_time)
            time.sleep(sleep_time)

    def call_llm(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        """Call the first available provider and return its response text."""

        global _last_llm_call_time
        self._respect_rate_limit()

        for provider in self._provider_order:
            try:
                if provider == "openai":
                    response = self._call_openai(prompt, model, temperature, max_tokens)
                elif provider == "anthropic":
                    response = self._call_anthropic(
                        prompt,
                        model="claude-3-sonnet-20240229",
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                elif provider == "mistral":
                    response = self._call_mistral(
                        prompt,
                        model="mistral-large-latest",
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                else:  # pragma: no cover - defensive
                    continue
                _last_llm_call_time = time.time()
                return response.strip()
            except Exception as exc:
                logger.error("LLM provider %s failed: %s", provider, exc)
                _last_llm_call_time = time.time()

        logger.error("All LLM providers failed to respond.")
        return "LLM Error: Unable to process the request."

    def _call_openai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        if self.openai_client is None:
            raise RuntimeError("OpenAI client is not configured")

        logger.debug("LLMClient(OpenAI): Calling model %s", model)
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            n=1,
        )
        return response.choices[0].message.content or ""

    def _call_anthropic(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        if self.anthropic_client is None:
            raise RuntimeError("Anthropic client is not configured")

        logger.debug("LLMClient(Anthropic): Calling model %s", model)
        response = self.anthropic_client.messages.create(
            model=model,
            system=self.system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        if not response.content:
            return ""
        # The content is a list of blocks; concatenate text blocks
        return "".join(block.text for block in response.content if hasattr(block, "text"))

    def _call_mistral(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        if self.mistral_client is None or ChatMessage is None:
            raise RuntimeError("Mistral client is not configured")

        logger.debug("LLMClient(Mistral): Calling model %s", model)
        response = self.mistral_client.chat(
            model=model,
            messages=[
                ChatMessage(role="system", content=self.system_prompt),
                ChatMessage(role="user", content=prompt),
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if not response.choices:
            return ""
        return response.choices[0].message.content or ""
