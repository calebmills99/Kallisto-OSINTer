"""Configuration helpers for Kallisto-OSINTer."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List


def _env_to_bool(value: str | None, default: bool = False) -> bool:
    """Coerce an environment string to a boolean."""

    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""

    if provider_order_env := os.getenv("LLM_PROVIDER_ORDER"):
        provider_order: List[str] = [
            item.strip().lower()
            for item in provider_order_env.split(",")
            if item.strip()
        ]
    else:
        provider_order = ["openai", "anthropic", "mistral", "kilocode"]

    config: Dict[str, Any] = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
        "MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY", ""),
        "KILOCODE_API_KEY": os.getenv("KILOCODE_API_KEY", ""),
        "KILOCODE_API_BASE": os.getenv("KILOCODE_API_BASE", "https://api.kilocode.com/v1"),
        "SERPER_API_KEY": os.getenv("SERPER_API_KEY", ""),
        "SCRAPINGBEE_API_KEY": os.getenv("SCRAPINGBEE_API_KEY", ""),
        "SCRAPING_DOG_API_KEY": os.getenv("SCRAPING_DOG_API_KEY", ""),
        "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY", ""),
        "CACHE_DIR": os.getenv("CACHE_DIR", "./cache"),
        "DEFAULT_USER_AGENT": os.getenv(
            "DEFAULT_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        ),
        "PROXY_LIST": os.getenv("PROXY_LIST", ""),
        "LLM_RATE_LIMIT": float(os.getenv("LLM_RATE_LIMIT", "2.0")),
        "SEARCH_RATE_LIMIT": float(os.getenv("SEARCH_RATE_LIMIT", "1.5")),
        "USERNAME_SEARCH_MAX_WORKERS": int(os.getenv("USERNAME_SEARCH_MAX_WORKERS", "10")),
        "LLM_PROVIDER_ORDER": provider_order,
        "LLM_MODEL_OVERRIDES": {
            "openai": os.getenv("LLM_MODEL_OPENAI", "gpt-3.5-turbo"),
            "anthropic": os.getenv("LLM_MODEL_ANTHROPIC", "claude-3-sonnet-20240229"),
            "mistral": os.getenv("LLM_MODEL_MISTRAL", "mistral-large-latest"),
            "kilocode": os.getenv("LLM_MODEL_KILOCODE", "gpt-3.5-turbo"),
        },
        "DEBUG_MODE": _env_to_bool(os.getenv("KALLISTO_DEBUG")),
        "LOG_LEVEL": os.getenv("KALLISTO_LOG_LEVEL"),
    }

    proxy_value = config["PROXY_LIST"]
    proxies: List[str]
    if not proxy_value:
        proxies = []
    else:
        try:
            loaded = json.loads(proxy_value)
        except json.JSONDecodeError:
            loaded = None

        if isinstance(loaded, list):
            proxies = [str(item).strip() for item in loaded if str(item).strip()]
        else:
            proxies = [
                item.strip()
                for item in proxy_value.split(",")
                if item.strip()
            ]

    config["PROXY_LIST"] = proxies

    if config["LOG_LEVEL"]:
        config["LOG_LEVEL"] = config["LOG_LEVEL"].upper()

    return config
