"""
Proxy validation utilities.
Checks a list of proxies to determine which ones are valid for making HTTP requests.
"""

import threading
import requests
from queue import Queue
from src.utils.logger import get_logger

logger = get_logger(__name__)

def validate_proxy(proxy, test_url="https://httpbin.org/ip", timeout=5):
    """
    Validates a single proxy by making a request to test_url.
    Returns True if the proxy works, else False.
    """
    try:
        response = requests.get(test_url, proxies={"http": proxy, "https": proxy}, timeout=timeout)
        if response.status_code == 200:
            logger.debug("Proxy %s validated.", proxy)
            return True
    except Exception as e:
        logger.debug("Proxy %s failed: %s", proxy, str(e))
    return False

def validate_proxies(proxy_list, test_url="https://httpbin.org/ip", timeout=5, max_threads=10):
    """
    Validates a list of proxies using threading.
    Returns a list of validated proxies.
    """
    valid_proxies = []
    q = Queue()
    threads = []

    def worker():
        while not q.empty():
            proxy = q.get()
            if validate_proxy(proxy, test_url=test_url, timeout=timeout):
                valid_proxies.append(proxy)
            q.task_done()

    for proxy in proxy_list:
        q.put(proxy)

    for _ in range(min(max_threads, len(proxy_list))):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    q.join()
    for t in threads:
        t.join()
    return valid_proxies