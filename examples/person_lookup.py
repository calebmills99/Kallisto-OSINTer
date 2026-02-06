#!/usr/bin/env python
"""
Example script that uses the KnowledgeAgent to perform a person lookup.
It accepts a person's name and a question as command-line arguments and outputs the final result.
"""

import argparse
import logging
from src.agents.knowledge_agent import KnowledgeAgent
from src.config import load_config
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    parser = argparse.ArgumentParser(description="Person Lookup using Kallisto-OSINTer")
    parser.add_argument("name", type=str, help="Name of the person to lookup")
    parser.add_argument(
        "--ask", type=str, default="Write a summary about this person", help="Final question to ask after gathering info"
    )
    parser.add_argument(
        "--rounds", type=int, default=2, help="Number of deep dive rounds"
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Validate required API keys
    if not config['OPENAI_API_KEY']:
        logging.error("OPENAI_API_KEY is not set in the environment.")
        return

    if not config['SERPER_API_KEY']:
        logging.error("SERPER_API_KEY is not set in the environment.")
        return

    # Create and run the knowledge agent
    knowledge_agent = KnowledgeAgent(query=args.name, config=config, rounds=args.rounds)

    # Aggregate knowledge through search and deep dives
    knowledge = knowledge_agent.aggregate_knowledge()

    # Answer the final question
    answer = knowledge_agent.answer_final_question(args.ask)

    # Display results
    print("\n" + "="*80)
    print(f"OSINT Report for: {args.name}")
    print("="*80)

    print("\n" + "-"*80)
    print("GATHERED INTELLIGENCE:")
    print("-"*80)
    print(knowledge)

    print("\n" + "="*80)
    print("FINAL ANSWER:")
    print("="*80)
    print(answer)
    print("="*80 + "\n")

    # Save results to file
    import os
    from datetime import datetime

    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/{args.name.replace(' ', '_')}_{timestamp}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"OSINT Report for: {args.name}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Question: {args.ask}\n")
        f.write("="*80 + "\n\n")
        f.write("GATHERED INTELLIGENCE:\n")
        f.write("-"*80 + "\n")
        f.write(knowledge + "\n\n")
        f.write("="*80 + "\n")
        f.write("FINAL ANSWER:\n")
        f.write("="*80 + "\n")
        f.write(answer + "\n")

    print(f"Results saved to: {filename}")


if __name__ == "__main__":
    main()