"""
Search tool module.
Uses the Serper API (or similar) to perform Google searches with optional filtering.
"""

import requests
from src.utils.logger import get_logger

logger = get_logger(__name__)

def search_query(query, config, country=None, language=None, date_range=None):
    """
    Performs a search query using the Serper API.
    Allows additional filtering parameters.
    Returns a list of search results with keys: 'title', 'link' and 'snippet'.
    """
    api_key = config.get('SERPER_API_KEY', '')
    url = "https://api.serper.dev/search"
    params = {
        "q": query,
        "api_key": api_key
    }
    # Add filters if provided
    if country:
        params["gl"] = country
    if language:
        params["hl"] = language
    if date_range:
        params["date"] = date_range

    logger.debug("Sending search query: %s", params)
    try:
        response = requests.get(url, params=params, timeout=10)
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