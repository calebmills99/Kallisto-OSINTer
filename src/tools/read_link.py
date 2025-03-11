"""
Read Link tool module.
Fetches the raw HTML content from a given URL using ScrapingBee.
Also integrates with chunking/summarization later.
"""

import requests
from src.utils.logger import get_logger

logger = get_logger(__name__)

def read_url(url, config):
    """
    Fetches a URL's content using the ScrapingBee API to bypass anti-bot measures.
    Returns raw HTML content as a string.
    """
    api_key = config.get('SCRAPINGBEE_API_KEY', '')
    scrapingbee_url = "https://app.scrapingbee.com/api/v1/"
    params = {
        "api_key": api_key,
        "url": url,
        "render_js": "true"
    }
    logger.debug("Reading URL via ScrapingBee: %s", url)
    try:
        response = requests.get(scrapingbee_url, params=params, timeout=15)
        if response.status_code == 200:
            return response.text
        else:
            logger.error("ScrapingBee error: %s", response.text)
            return ""
    except Exception as e:
        logger.error("Exception fetching URL %s: %s", url, str(e))
        return ""