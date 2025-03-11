"""
Username Search module.
Searches a list of URLs concurrently for a specified username.
Utilizes threading, proxies, and randomized user agents.
"""

import threading
import requests
from src.utils.proxies import validate_proxies
from src.utils.user_agents import get_random_user_agent
from src.utils.logger import get_logger

logger = get_logger(__name__)

def search_username(username, urls, config):
    """
    For each URL, check if the username appears in the content.
    Returns a list of dictionaries with URL and HTTP status.
    """
    results = []
    threads = []
    lock = threading.Lock()

    # Validate proxies if available
    proxy_list = config.get("PROXY_LIST", [])
    valid_proxies = validate_proxies(proxy_list) if proxy_list else []

    def worker(url):
        headers = {"User-Agent": get_random_user_agent()}
        proxy = {"http": valid_proxies[0], "https": valid_proxies[0]} if valid_proxies else None
        try:
            response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
            content = response.text
            found = username.lower() in content.lower()
            status = "found" if found else "not found"
        except Exception as e:
            status = f"error: {str(e)}"
        with lock:
            results.append({"url": url, "status": status})

    for url in urls:
        t = threading.Thread(target=worker, args=(url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return results