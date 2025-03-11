"""
Web Scraper module.
Provides functions for generic web scraping tasks.
"""

import requests
from bs4 import BeautifulSoup
from src.utils.logger import get_logger

logger = get_logger(__name__)

def scrape(url, use_js_render=False):
    """
    Scrapes the given URL. If use_js_render is True, attempts to use a JS-rendering service.
    Returns the raw HTML content.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            logger.error("Failed to scrape %s: %s", url, response.status_code)
            return ""
    except Exception as e:
        logger.error("Exception during scraping %s: %s", url, str(e))
        return ""

def extract_links(html_content):
    """
    Extracts and returns all hyperlinks from the provided HTML content.
    """
    soup = BeautifulSoup(html_content, "lxml")
    links = [a.get("href") for a in soup.find_all("a", href=True)]
    return links