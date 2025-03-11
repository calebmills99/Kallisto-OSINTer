"""
Deep Dive Agent module.
Extends the WebAgent with a deep dive topic to target specific areas.
"""

from src.agents.web_agent import WebAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DeepDiveAgent(WebAgent):
    def __init__(self, query, config, deep_dive_topic):
        super().__init__(query, config, deep_dive_topic)
        self.deep_dive_topic = deep_dive_topic

    def perform_search(self):
        """
        Overrides search to include the deep dive topic.
        """
        deep_query = f"{self.query} {self.deep_dive_topic}"
        logger.info("DeepDiveAgent: Searching for deep dive query: %s", deep_query)
        try:
            self.results = __import__('src.tools.search', fromlist=['search_query']).search_query(deep_query, config=self.config)
        except Exception as e:
            logger.error("Deep dive search failed: %s", str(e))
            self.results = []

    # Inherits fetch_and_summarize and run from WebAgent unchanged.