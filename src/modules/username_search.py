"""Username Search module.

Searches a list of URLs concurrently for a specified username. Utilises
threading, proxies, and randomized user agents.
"""

from __future__ import annotations

import threading
from typing import Dict, List

import requests

from src.utils.logger import get_logger
from src.utils.proxies import validate_proxies
from src.utils.user_agents import get_random_user_agent

logger = get_logger(__name__)


def search_username(username: str, urls: List[str], config: dict) -> List[Dict[str, str]]:
    """Check each URL for ``username`` and return discovery metadata."""

    results: List[Dict[str, str]] = []
    threads = []
    lock = threading.Lock()

    proxy_list = config.get("PROXY_LIST", [])
    valid_proxies = validate_proxies(proxy_list) if proxy_list else []

    def worker(url: str) -> None:
        headers = {"User-Agent": get_random_user_agent()}
        proxy = {"http": valid_proxies[0], "https": valid_proxies[0]} if valid_proxies else None
        try:
            response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
            content = response.text
            found = username.lower() in content.lower()
            status = "found" if found else "not found"
        except Exception as exc:  # pragma: no cover - network/requests failures
            status = f"error: {exc}"
        with lock:
            results.append({"url": url, "status": status})

    for url in urls:
        thread = threading.Thread(target=worker, args=(url,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return results
