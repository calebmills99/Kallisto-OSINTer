"""
Caching utilities for Kallisto-OSINTer.
Provides both in-memory and file-based caching for expensive operations.
"""

import os
import pickle
import threading
from time import time

class Cache:
    _lock = threading.Lock()
    _memory_cache = {}

    def __init__(self, cache_dir="./cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _get_cache_path(self, key):
        safe_key = key.replace("/", "_")
        return os.path.join(self.cache_dir, f"{safe_key}.pkl")

    def get(self, key, max_age=3600):
        """
        Retrieves a cached value if it exists and is not older than max_age seconds.
        """
        with Cache._lock:
            if key in Cache._memory_cache:
                value, timestamp = Cache._memory_cache[key]
                if time() - timestamp < max_age:
                    return value

            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, "rb") as f:
                        value, timestamp = pickle.load(f)
                        if time() - timestamp < max_age:
                            Cache._memory_cache[key] = (value, timestamp)
                            return value
                except Exception as e:
                    # In case of any error, treat as cache miss.
                    pass
            return None

    def set(self, key, value):
        """
        Caches a value in both in-memory and file-based caches.
        """
        with Cache._lock:
            timestamp = time()
            Cache._memory_cache[key] = (value, timestamp)
            cache_path = self._get_cache_path(key)
            try:
                with open(cache_path, "wb") as f:
                    pickle.dump((value, timestamp), f)
            except Exception as e:
                # If writing to file fails, continue using in-memory cache.
                pass

    def clear(self):
        """
        Clears the entire cache.
        """
        with Cache._lock:
            Cache._memory_cache.clear()
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    continue

# Example usage:
# cache = Cache()
# result = cache.get("some_key")
# if result is None:
#     result = expensive_computation()
#     cache.set("some_key", result)