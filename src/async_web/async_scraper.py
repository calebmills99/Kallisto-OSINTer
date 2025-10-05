"""
Asynchronous Web Scraper module.
Uses aiohttp and httpx to perform asynchronous web scraping.
Supports proxy rotation and randomized user agents.
"""

import asyncio
import aiohttp
import httpx
import random
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_fixed

from src.utils.user_agents import get_random_user_agent
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AsyncRateLimiter:
    """Simple asyncio-compatible rate limiter."""

    def __init__(self, interval: float):
        self._interval = max(0.0, float(interval))
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def acquire(self) -> None:
        """Waits until the next call is allowed based on the interval."""
        if self._interval <= 0:
            return

        async with self._lock:
            loop = asyncio.get_running_loop()
            now = loop.time()
            wait_time = self._last_call + self._interval - now
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                now = loop.time()
            self._last_call = now


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
async def async_fetch(
    url,
    proxy=None,
    *,
    session: Optional[aiohttp.ClientSession] = None,
    semaphore: Optional[asyncio.Semaphore] = None,
    rate_limiter: Optional[AsyncRateLimiter] = None,
):
    """
    Retries fetching a URL asynchronously with aiohttp.
    """
    async def _do_fetch(client_session: aiohttp.ClientSession):
        if rate_limiter:
            await rate_limiter.acquire()
        if semaphore:
            async with semaphore:
                return await fetch_url(client_session, url, proxy=proxy)
        return await fetch_url(client_session, url, proxy=proxy)

    if session is not None:
        return await _do_fetch(session)

    async with aiohttp.ClientSession() as own_session:
        return await _do_fetch(own_session)

async def fetch_all(urls, proxies=None, *, max_concurrent=5, rate_limit_interval=0.0):
    """
    Fetches multiple URLs asynchronously.
    Rotates proxies if provided.
    """
    semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
    rate_limiter = AsyncRateLimiter(rate_limit_interval) if rate_limit_interval else None

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            proxy = random.choice(proxies) if proxies else None
            tasks.append(
                async_fetch(
                    url,
                    proxy,
                    session=session,
                    semaphore=semaphore,
                    rate_limiter=rate_limiter,
                )
            )
        results = await asyncio.gather(*tasks)
    return results

def async_scrape_urls(urls, proxies=None, *, max_concurrent=5, rate_limit_interval=0.0):
    """
    Synchronous wrapper to scrape URLs asynchronously.
    """
    return asyncio.run(
        fetch_all(
            urls,
            proxies,
            max_concurrent=max_concurrent,
            rate_limit_interval=rate_limit_interval,
        )
    )


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

async def httpx_fetch_all(urls, proxies=None, *, max_concurrent=5, rate_limit_interval=0.0):
    """
    Fetches multiple URLs asynchronously using httpx.
    """
    semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
    rate_limiter = AsyncRateLimiter(rate_limit_interval) if rate_limit_interval else None

    async def _wrapped_fetch(url, proxy):
        if rate_limiter:
            await rate_limiter.acquire()
        if semaphore:
            async with semaphore:
                return await httpx_fetch(url, proxy)
        return await httpx_fetch(url, proxy)

    tasks = []
    for url in urls:
        proxy = random.choice(proxies) if proxies else None
        tasks.append(_wrapped_fetch(url, proxy))
    results = await asyncio.gather(*tasks)
    return results

def async_scrape_urls_httpx(urls, proxies=None, *, max_concurrent=5, rate_limit_interval=0.0):
    """
    Synchronous wrapper for httpx asynchronous scraping.
    """
    return asyncio.run(
        httpx_fetch_all(
            urls,
            proxies,
            max_concurrent=max_concurrent,
            rate_limit_interval=rate_limit_interval,
        )
    )
