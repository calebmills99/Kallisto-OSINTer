"""
Person Lookup module.
Given a person's name and a task (question), uses the KnowledgeAgent to gather information and then answers the question.
"""

from src.agents.knowledge_agent import KnowledgeAgent
from src.llm.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

def lookup_person(name, question, config):
    """
    Lookup a person by:
      1. Using the KnowledgeAgent to gather information.
      2. Feeding the full knowledge base to the LLM client to answer the question.
    """
    logger.info("Initiating person lookup for: %s", name)
    # Prepare initial query and instantiate KnowledgeAgent
    query = f"Learn as much as you can about {name}"
    knowledge_agent = KnowledgeAgent(query, config, rounds=2)
    full_knowledge = knowledge_agent.aggregate_knowledge()
    
    # Answer the question using the aggregated knowledge
    answer = knowledge_agent.answer_final_question(question)
    
    # Optionally, format answer (e.g., create markdown resume, tables, etc.)
    # For now, we simply return the answer
    return answer