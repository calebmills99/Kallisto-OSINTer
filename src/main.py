"""
Main entry point for Kallisto-OSINTer.
This script sets up the configuration, initializes logging and parses command-line arguments to trigger various OSINT tasks.
"""

import argparse
import sys
import os
from src.config import load_config
from src.modules import person_lookup, username_search
from src.agents.knowledge_agent import KnowledgeAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Kallisto-OSINTer: LLM-based OSINT tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Person lookup command
    lookup_parser = subparsers.add_parser("person_lookup", help="Lookup a person")
    lookup_parser.add_argument("name", type=str, help="Name of the person to lookup")
    lookup_parser.add_argument("--ask", type=str, required=True, help="Task to perform on the person info")

    # Username search command
    uname_parser = subparsers.add_parser("username_search", help="Search for a username across URLs")
    uname_parser.add_argument("username", type=str, help="Username to search")
    uname_parser.add_argument("--urls", type=str, nargs='+', required=True, help="List of URLs to search in")

    return parser.parse_args()

def main():
    config = load_config()
    args = parse_arguments()

    if args.command == "person_lookup":
        logger.info("Starting person lookup for %s", args.name)
        result = person_lookup.lookup_person(args.name, args.ask, config)
        print(result)
    elif args.command == "username_search":
        logger.info("Starting username search for %s", args.username)
        results = username_search.search_username(args.username, args.urls, config)
        for res in results:
            print(f"URL: {res['url']}, Status: {res['status']}")
    else:
        logger.error("Unknown command: %s", args.command)
        sys.exit(1)

if __name__ == "__main__":
    main()