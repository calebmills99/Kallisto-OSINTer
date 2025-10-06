"""LLM Client module.

Wraps calls to available large language model providers with rate limiting and
fallback behaviour. The client will attempt to use OpenAI first, then Anthropic
and finally Mistral if earlier providers fail.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

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
_SUPPORTED_PROVIDERS = ("openai", "anthropic", "mistral")
_DEFAULT_PROVIDER_ORDER = list(_SUPPORTED_PROVIDERS)
_DEFAULT_PROVIDER_MODELS = {
    "openai": "gpt-4",
    "anthropic": "claude-3-sonnet-20240229",
    "mistral": "mistral-large-latest",
}


class LLMClient:
    """Wrapper around multiple LLM providers with fallback support."""

    def __init__(
        self,
        openai_key: Optional[str] = None,
        anthropic_key: Optional[str] = None,
        mistral_key: Optional[str] = None,
        provider_order: Optional[Sequence[str]] = None,
        models: Optional[Dict[str, str]] = None,
        rate_limit: float = 2.0,
        system_prompt: str = _DEFAULT_SYSTEM_PROMPT,
    ) -> None:
        self._rate_limit_lock = threading.Lock()
        self._last_llm_call_time = 0.0
        self.rate_limit = max(rate_limit, 0.0)
        self.system_prompt = system_prompt

        self.openai_key = openai_key or ""
        self.anthropic_key = anthropic_key or ""
        self.mistral_key = mistral_key or ""
        self._provider_models: Dict[str, str] = dict(_DEFAULT_PROVIDER_MODELS)
        if models:
            for name, value in models.items():
                if not value:
                    continue
                normalised = name.lower()
                if normalised in _SUPPORTED_PROVIDERS:
                    self._provider_models[normalised] = value

        self.openai_client = self._build_client(self.openai_key, OpenAI, "OpenAI")
        self.anthropic_client = self._build_client(self.anthropic_key, Anthropic, "Anthropic")
        self.mistral_client = self._build_client(self.mistral_key, MistralClient, "Mistral")

        order = self._normalise_provider_order(provider_order)
        provider_map: Dict[str, tuple[Any, Callable[[str, str, float, int], str]]] = {
            "openai": (self.openai_client, self._call_openai),
            "anthropic": (self.anthropic_client, self._call_anthropic),
            "mistral": (self.mistral_client, self._call_mistral),
        }

        self._providers: List[tuple[str, Callable[[str, str, float, int], str]]] = []
        for name in order:
            client, call_fn = provider_map.get(name, (None, None))
            if client is None:
                continue
            self._providers.append((name, call_fn))

        if not self._providers:
            logger.warning("LLMClient initialized without any available providers.")

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "LLMClient":
        """Instantiate the client using a configuration dictionary."""

        return cls(
            openai_key=config.get("OPENAI_API_KEY"),
            anthropic_key=config.get("ANTHROPIC_API_KEY"),
            mistral_key=config.get("MISTRAL_API_KEY"),
            rate_limit=float(config.get("LLM_RATE_LIMIT", 2.0)),
            provider_order=config.get("LLM_PROVIDER_ORDER"),
            models=config.get("LLM_MODEL_OVERRIDES"),
            system_prompt=config.get("LLM_SYSTEM_PROMPT", _DEFAULT_SYSTEM_PROMPT),
        )

    def _respect_rate_limit(self) -> None:
        if self.rate_limit <= 0:
            return
        with self._rate_limit_lock:
            elapsed = time.time() - self._last_llm_call_time
            if elapsed < self.rate_limit:
                sleep_time = self.rate_limit - elapsed
                logger.debug("LLM rate limiting: sleeping for %.2f seconds", sleep_time)
                time.sleep(sleep_time)
            self._last_llm_call_time = time.time()

    def _record_call_time(self) -> None:
        if self.rate_limit <= 0:
            return
        with self._rate_limit_lock:
            self._last_llm_call_time = time.time()

    @staticmethod
    def _normalise_provider_order(provider_order: Optional[Sequence[str]] | Optional[str]) -> List[str]:
        if provider_order is None:
            candidates: Iterable[str] = _DEFAULT_PROVIDER_ORDER
        elif isinstance(provider_order, str):
            candidates = [part.strip() for part in provider_order.split(",")]
        else:
            candidates = provider_order

        order: List[str] = []
        for candidate in candidates:
            name = candidate.strip().lower()
            if not name:
                continue
            if name not in _SUPPORTED_PROVIDERS:
                logger.warning("Ignoring unsupported LLM provider '%s' in configuration.", candidate)
                continue
            if name not in order:
                order.append(name)
        return order or list(_DEFAULT_PROVIDER_ORDER)

    def _build_client(self, key: str, cls: Any, provider_name: str) -> Optional[Any]:
        if not key or cls is None:
            return None
        try:
            return cls(api_key=key)
        except Exception as exc:  # pragma: no cover - network failures
            logger.error("Failed to initialize %s client: %s", provider_name, exc)
            return None

    def call_llm(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        model_overrides: Optional[Dict[str, str]] = None,
    ) -> str:
        """Call the first available provider and return its response text."""

        self._respect_rate_limit()

        if not self._providers:
            logger.error("All LLM providers failed to respond.")
            return "LLM Error: Unable to process the request."

        provider_models = dict(self._provider_models)
        if model:
            provider_models["openai"] = model
        if model_overrides:
            for name, override in model_overrides.items():
                if not override:
                    continue
                provider_models[name.lower()] = override

        for provider, call_fn in self._providers:
            try:
                provider_model = provider_models.get(provider) or model or ""
                response = call_fn(prompt, provider_model, temperature, max_tokens)
                self._record_call_time()
                return (response or "").strip()
            except Exception as exc:
                logger.error("LLM provider %s failed: %s", provider, exc)
                self._record_call_time()

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
        if not getattr(response, "choices", None):
            return ""
        message = response.choices[0].message
        return getattr(message, "content", "") or ""

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
        return response.choices[0].message.content or "" if response.choices else ""
