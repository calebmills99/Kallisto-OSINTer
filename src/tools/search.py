"""
Search tool module.
Uses the Serper API (or similar) to perform Google searches with optional filtering.
"""

import requests
import time
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Rate limiting state
_last_search_time = 0
_min_search_interval = 1.5  # minimum seconds between searches

def search_query(query, config, country=None, language=None, date_range=None):
    """
    Performs a search query using the Serper API.
    Allows additional filtering parameters.
    Returns a list of search results with keys: 'title', 'link' and 'snippet'.
    """
    api_key = config.get('SERPER_API_KEY', '')
    url = "https://google.serper.dev/search"

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "q": query
    }

    # Add filters if provided
    if country:
        payload["gl"] = country
    if language:
        payload["hl"] = language
    if date_range:
        payload["tbs"] = date_range

    # Rate limiting
    global _last_search_time
    current_time = time.time()
    time_since_last = current_time - _last_search_time
    if time_since_last < _min_search_interval:
        sleep_time = _min_search_interval - time_since_last
        logger.debug("Rate limiting: sleeping for %.2f seconds", sleep_time)
        time.sleep(sleep_time)

    logger.debug("Sending search query: %s", payload)
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        _last_search_time = time.time()
        if response.status_code == 200:
            data = response.json()
            # Parse results into a list of dicts
            results = []
            for item in data.get("organic", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
            return results
        else:
            logger.error("Search API error: %s", response.text)
            return []
    except Exception as e:
        logger.error("Exception during search: %s", str(e))
        return []