#!/usr/bin/env python
"""
Example script that uses the KnowledgeAgent to perform a person lookup.
It accepts a person's name and a question as command-line arguments and outputs the final result.
"""

import argparse
import logging
from src.tools.llm import LLMClient
from src.tools.web_agent import WebAgent
from src.tools.knowledge_agent import KnowledgeAgent
from dotenv import load_dotenv
import os

# Load environment variables from .env file if present
load_dotenv()

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    parser = argparse.ArgumentParser(description="Person Lookup using Kallisto-OSINTer")
    parser.add_argument("name", type=str, help="Name of the person to lookup")
    parser.add_argument(
        "--ask", type=str, default="Write a summary about this person", help="Final question to ask after gathering info"
    )
    args = parser.parse_args()

    # Initialize LLM client and web agent
    try:
        llm_client = LLMClient(model="gpt-4", max_tokens=1024)
    except Exception as e:
        logging.error(f"Error initializing LLMClient: {e}")
        return

    scrapingbee_key = os.getenv("SCRAPINGBEE_API_KEY")
    if not scrapingbee_key:
        logging.error("SCRAPINGBEE_API_KEY is not set in the environment.")
        return

    try:
        web_agent = WebAgent(llm_client=llm_client, scrapingbee_api_key=scrapingbee_key)
    except Exception as e:
        logging.error(f"Error initializing WebAgent: {e}")
        return

    # Create and run the knowledge agent
    knowledge_agent = KnowledgeAgent(subject=args.name, llm_client=llm_client, web_agent=web_agent)
    final_result = knowledge_agent.run()

    # Append the final question prompt and ask the LLM
    final_prompt = f"{args.ask}\n\nBased on the gathered information:\n{final_result}"
    answer = llm_client.call_llm(prompt=final_prompt, context=final_result)
    print("Final Answer:\n")
    print(answer)


if __name__ == "__main__":
    main()