"""
Web Agent module.
This agent is responsible for performing searches and scraping content from the web.
It integrates search, read_link and LLM summarization.
"""

import time
import threading
from src.tools import search, read_link, llm_map_reduce
from src.llm.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

class WebAgent:
    def __init__(self, query, config, deep_dive_topic=None):
        self.query = query
        self.config = config
        self.deep_dive_topic = deep_dive_topic
        self.llm_client = LLMClient(config['OPENAI_API_KEY'])
        self.results = []
        self.summary = ""
        self.lock = threading.Lock()

    def perform_search(self):
        """
        Performs a search using the serper API.
        """
        logger.info("WebAgent: Performing search for query: %s", self.query)
        try:
            self.results = search.search_query(self.query, config=self.config)
        except Exception as e:
            logger.error("Search failed: %s", str(e))
            self.results = []

    def fetch_and_summarize(self, url):
        """
        Uses read_link to get page content, then applies llm_map_reduce to summarize.
        """
        logger.info("WebAgent: Fetching and summarizing URL: %s", url)
        try:
            html_content = read_link.read_url(url, config=self.config)
            summary = llm_map_reduce.map_reduce(html_content, self.llm_client)
            with self.lock:
                self.summary += f"\nURL: {url}\nSummary: {summary}\n"
        except Exception as e:
            logger.error("Failed to fetch or summarize %s: %s", url, str(e))

    def run(self):
        """
        Runs the full workflow: search, then fetch and summarize results.
        """
        self.perform_search()
        threads = []
        for result in self.results:
            t = threading.Thread(target=self.fetch_and_summarize, args=(result['link'],))
            t.start()
            threads.append(t)
            time.sleep(1.0)  # increased delay to avoid rate limiting

        for t in threads:
            t.join()
        return self.summary