"""
Read Link tool module.
Fetches the raw HTML content from a given URL using multiple scraping services.
Supports ScrapingBee, ScrapingDog, Firecrawl, and direct requests as fallback.
"""

import requests
from src.utils.logger import get_logger

logger = get_logger(__name__)

def _try_firecrawl(url, api_key):
    """Try fetching URL using Firecrawl API."""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {"url": url}
        response = requests.post("https://api.firecrawl.dev/v0/scrape",
                                json=data, headers=headers, timeout=15)
        if response.status_code == 200:
            result = response.json()
            return result.get('data', {}).get('html', '')
    except Exception as e:
        logger.debug("Firecrawl failed: %s", str(e))
    return None

def _try_scrapingdog(url, api_key):
    """Try fetching URL using ScrapingDog API."""
    try:
        params = {"api_key": api_key, "url": url, "dynamic": "true"}
        response = requests.get("https://api.scrapingdog.com/scrape",
                              params=params, timeout=15)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        logger.debug("ScrapingDog failed: %s", str(e))
    return None

def _try_scrapingbee(url, api_key):
    """Try fetching URL using ScrapingBee API."""
    try:
        params = {"api_key": api_key, "url": url, "render_js": "true"}
        response = requests.get("https://app.scrapingbee.com/api/v1/",
                              params=params, timeout=15)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        logger.debug("ScrapingBee failed: %s", str(e))
    return None

def read_url(url, config):
    """
    Fetches a URL's content using multiple scraping services with automatic fallback.
    Tries: Firecrawl -> ScrapingDog -> ScrapingBee -> Direct Request
    Returns raw HTML content as a string.
    """
    # Try Firecrawl first
    if config.get('FIRECRAWL_API_KEY'):
        logger.debug("Trying Firecrawl for: %s", url)
        content = _try_firecrawl(url, config['FIRECRAWL_API_KEY'])
        if content:
            return content

    # Try ScrapingDog
    if config.get('SCRAPING_DOG_API_KEY'):
        logger.debug("Trying ScrapingDog for: %s", url)
        content = _try_scrapingdog(url, config['SCRAPING_DOG_API_KEY'])
        if content:
            return content

    # Try ScrapingBee
    if config.get('SCRAPINGBEE_API_KEY'):
        logger.debug("Trying ScrapingBee for: %s", url)
        content = _try_scrapingbee(url, config['SCRAPINGBEE_API_KEY'])
        if content:
            return content

    # Fallback to direct request
    logger.debug("Trying direct request for: %s", url)
    try:
        headers = {
            'User-Agent': config.get('DEFAULT_USER_AGENT',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.text
        logger.warning("Direct request failed with status %d for %s",
                      response.status_code, url)
    except Exception as e:
        logger.error("All scraping methods failed for %s: %s", url, str(e))

    return ""