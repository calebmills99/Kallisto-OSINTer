"""
Unit tests for Asynchronous Web Scraper module.
"""

import unittest
from src.async_web.async_scraper import async_scrape_urls, async_scrape_urls_httpx

class TestAsyncScraper(unittest.TestCase):
    def test_async_scrape_urls(self):
        urls = ["https://httpbin.org/get", "https://httpbin.org/status/404"]
        results = async_scrape_urls(urls)
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn("url", result)
            self.assertIn("status", result)
    
    def test_async_scrape_urls_httpx(self):
        urls = ["https://httpbin.org/get", "https://httpbin.org/status/404"]
        results = async_scrape_urls_httpx(urls)
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn("url", result)
            self.assertIn("status", result)

if __name__ == "__main__":
    unittest.main()