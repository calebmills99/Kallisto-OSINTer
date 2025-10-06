"""Configuration helpers for Kallisto-OSINTer."""

from __future__ import annotations

import json
import os
from typing import Any, Dict


def _env_to_bool(value: str | None, default: bool = False) -> bool:
    """Coerce an environment string to a boolean."""

    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""

    config: Dict[str, Any] = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
        "MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY", ""),
        "SERPER_API_KEY": os.getenv("SERPER_API_KEY", ""),
        "SCRAPINGBEE_API_KEY": os.getenv("SCRAPINGBEE_API_KEY", ""),
        "SCRAPING_DOG_API_KEY": os.getenv("SCRAPING_DOG_API_KEY", ""),
        "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY", ""),
        "CACHE_DIR": os.getenv("CACHE_DIR", "./cache"),
        "DEFAULT_USER_AGENT": os.getenv(
            "DEFAULT_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        ),
        "PROXY_LIST": os.getenv("PROXY_LIST", "[]"),
        "LLM_RATE_LIMIT": float(os.getenv("LLM_RATE_LIMIT", "2.0")),
        "SEARCH_RATE_LIMIT": float(os.getenv("SEARCH_RATE_LIMIT", "1.5")),
        "DEBUG_MODE": _env_to_bool(os.getenv("KALLISTO_DEBUG")),
        "LOG_LEVEL": os.getenv("KALLISTO_LOG_LEVEL"),
    }

    try:
        config["PROXY_LIST"] = json.loads(config["PROXY_LIST"])
    except Exception:
        config["PROXY_LIST"] = []

    if config["LOG_LEVEL"]:
        config["LOG_LEVEL"] = config["LOG_LEVEL"].upper()

    return config
