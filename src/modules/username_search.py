"""Username Search module.

Searches a list of URLs concurrently for a specified username. Utilises
threading, proxies, and randomized user agents.
"""

from __future__ import annotations

import random
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

import requests

from src.utils.logger import get_logger
from src.utils.proxies import validate_proxies
from src.utils.user_agents import get_random_user_agent

logger = get_logger(__name__)


def search_username(username: str, urls: List[str], config: dict) -> List[Dict[str, str]]:
    """Check each URL for ``username`` and return discovery metadata."""

    proxy_list = config.get("PROXY_LIST", [])
    valid_proxies = validate_proxies(proxy_list) if proxy_list else []
    max_workers_config = int(config.get("USERNAME_SEARCH_MAX_WORKERS", 10))
    worker_count = max(1, min(max_workers_config, len(urls) or 1))

    def worker(url: str) -> Dict[str, str]:
        headers = {"User-Agent": get_random_user_agent()}
        proxy_address = random.choice(valid_proxies) if valid_proxies else None
        proxy = {"http": proxy_address, "https": proxy_address} if proxy_address else None
        try:
            response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
            content = response.text
            found = username.lower() in content.lower()
            status = "found" if found else "not found"
        except Exception as exc:  # pragma: no cover - network/requests failures
            status = f"error: {exc}"
        return {"url": url, "status": status}

    if not urls:
        return []

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        return list(executor.map(worker, urls))
