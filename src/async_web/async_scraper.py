"""
Asynchronous Web Scraper module.
Uses aiohttp and httpx to perform asynchronous web scraping.
Supports proxy rotation and randomized user agents.
"""

import asyncio
import aiohttp
import httpx
import random
from tenacity import retry, stop_after_attempt, wait_fixed
from src.utils.user_agents import get_random_user_agent
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def fetch_url(session, url, proxy=None, timeout=10):
    """
    Asynchronously fetches a URL using aiohttp.
    """
    headers = {"User-Agent": get_random_user_agent()}
    try:
        async with session.get(url, proxy=proxy, headers=headers, timeout=timeout) as response:
            text = await response.text()
            logger.info("Fetched URL: %s with status: %s", url, response.status)
            return {"url": url, "status": response.status, "content": text}
    except Exception as e:
        logger.error("Error fetching URL %s: %s", url, str(e))
        return {"url": url, "status": "error", "content": ""}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def async_fetch(url, proxy=None):
    """
    Retries fetching a URL asynchronously with aiohttp.
    """
    async with aiohttp.ClientSession() as session:
        result = await fetch_url(session, url, proxy=proxy)
        return result

async def fetch_all(urls, proxies=None):
    """
    Fetches multiple URLs asynchronously.
    Rotates proxies if provided.
    """
    tasks = []
    for url in urls:
        proxy = None
        if proxies:
            proxy = random.choice(proxies)
        tasks.append(async_fetch(url, proxy))
    results = await asyncio.gather(*tasks)
    return results

def async_scrape_urls(urls, proxies=None):
    """
    Synchronous wrapper to scrape URLs asynchronously.
    """
    return asyncio.run(fetch_all(urls, proxies))

async def httpx_fetch(url, proxy=None, timeout=10):
    """
    Fetches a URL asynchronously using httpx.
    """
    headers = {"User-Agent": get_random_user_agent()}
    proxies = {"http://": proxy, "https://": proxy} if proxy else None
    async with httpx.AsyncClient(proxies=proxies, timeout=timeout) as client:
        try:
            response = await client.get(url, headers=headers)
            logger.info("HTTPX fetched URL: %s with status: %s", url, response.status_code)
            return {"url": url, "status": response.status_code, "content": response.text}
        except Exception as e:
            logger.error("HTTPX error fetching URL %s: %s", url, str(e))
            return {"url": url, "status": "error", "content": ""}

async def httpx_fetch_all(urls, proxies=None):
    """
    Fetches multiple URLs asynchronously using httpx.
    """
    tasks = []
    for url in urls:
        proxy = None
        if proxies:
            proxy = random.choice(proxies)
        tasks.append(httpx_fetch(url, proxy))
    results = await asyncio.gather(*tasks)
    return results

def async_scrape_urls_httpx(urls, proxies=None):
    """
    Synchronous wrapper for httpx asynchronous scraping.
    """
    return asyncio.run(httpx_fetch_all(urls, proxies))