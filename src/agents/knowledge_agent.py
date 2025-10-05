"""
Knowledge Agent module.
Orchestrates the overall OSINT task by coordinating web agents.
It spawns initial and deep-dive agents based on the gathered information.
"""

import time
import threading
from src.agents.web_agent import WebAgent
from src.agents.deep_dive_agent import DeepDiveAgent
from src.llm.llm_client import LLMClient
from src.llm.prompt_templates import PROMPT_GATHER, PROMPT_DEEP_DIVE, PROMPT_SUMMARY
from src.utils.logger import get_logger

logger = get_logger(__name__)

class KnowledgeAgent:
    def __init__(self, query, config, rounds=2):
        self.query = query
        self.config = config
        self.rounds = rounds
        self.llm_client = LLMClient(config['OPENAI_API_KEY'])
        self.full_knowledge = ""

    def spawn_initial_agent(self):
        logger.info("KnowledgeAgent: Spawning initial web agent.")
        agent = WebAgent(query=self.query, config=self.config)
        initial_summary = agent.run()
        return initial_summary

    def spawn_deep_dive_agents(self, topics):
        logger.info("KnowledgeAgent: Spawning deep dive agents for topics: %s", topics)
        summaries = []
        threads = []
        lock = threading.Lock()

        def run_agent(topic):
            agent = DeepDiveAgent(query=self.query, config=self.config, deep_dive_topic=topic)
            summary = agent.run()
            with lock:
                summaries.append((topic, summary))

        for topic in topics:
            t = threading.Thread(target=run_agent, args=(topic,))
            t.start()
            threads.append(t)
            time.sleep(2.0)  # increased delay to avoid rate limiting

        for t in threads:
            t.join()
        return summaries

    def determine_deep_dive_topics(self, current_knowledge):
        """
        Uses the LLM client with a prompt template to determine deep-dive topics.
        """
        prompt = PROMPT_DEEP_DIVE.format(knowledge=current_knowledge)
        response = self.llm_client.call_llm(prompt)
        topics = [t.strip() for t in response.split(",") if t.strip()]
        logger.info("Determined deep dive topics: %s", topics)
        return topics

    def aggregate_knowledge(self):
        logger.info("KnowledgeAgent: Aggregating knowledge...")
        initial_knowledge = self.spawn_initial_agent()
        self.full_knowledge += f"Initial Knowledge:\n{initial_knowledge}\n"

        for r in range(self.rounds):
            logger.info("KnowledgeAgent: Deep dive round %d", r+1)
            topics = self.determine_deep_dive_topics(self.full_knowledge)
            deep_dive_summaries = self.spawn_deep_dive_agents(topics)
            for topic, summary in deep_dive_summaries:
                self.full_knowledge += f"\nDeep Dive on {topic}:\n{summary}\n"
        return self.full_knowledge

    def answer_final_question(self, question):
        """
        Uses the aggregated knowledge and a final prompt to answer a question.
        """
        prompt = PROMPT_SUMMARY.format(knowledge=self.full_knowledge, question=question)
        answer = self.llm_client.call_llm(prompt)
        return answer