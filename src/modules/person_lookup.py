"""Person Lookup module.

Given a person's name and a task (question), uses the KnowledgeAgent to gather
information and then answers the question.
"""

from __future__ import annotations

from src.agents.knowledge_agent import KnowledgeAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)


def lookup_person(name: str, question: str, config: dict) -> str:
    """Return an answer about ``name`` based on the supplied ``question``."""

    logger.info("Initiating person lookup for: %s", name)
    query = f"Learn as much as you can about {name}"
    knowledge_agent = KnowledgeAgent(query, config, rounds=2)
    knowledge_agent.aggregate_knowledge()
    answer = knowledge_agent.answer_final_question(question)
    return answer
