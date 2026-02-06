"""
Unit tests for agent modules.
Tests basic functionality of the KnowledgeAgent and WebAgent.
"""

import unittest
from src.agents.knowledge_agent import KnowledgeAgent
from src.config import load_config

class TestAgents(unittest.TestCase):
    def setUp(self):
        self.config = load_config()
        self.config['OPENAI_API_KEY'] = "dummy_key"  # For testing purposes
        self.query = "Learn as much as you can about John Doe"

    def test_knowledge_agent_aggregate(self):
        agent = KnowledgeAgent(query=self.query, config=self.config, rounds=1)
        knowledge = agent.aggregate_knowledge()
        self.assertIsInstance(knowledge, str)
        self.assertGreater(len(knowledge), 0)

    def test_knowledge_agent_final_answer(self):
        agent = KnowledgeAgent(query=self.query, config=self.config, rounds=1)
        agent.full_knowledge = "Test knowledge base."
        answer = agent.answer_final_question("What do you know?")
        self.assertIsInstance(answer, str)
        self.assertGreater(len(answer), 0)

if __name__ == "__main__":
    unittest.main()