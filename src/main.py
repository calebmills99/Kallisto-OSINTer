"""Main entry point for Kallisto-OSINTer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from src.config import load_config
from src.modules import person_lookup, username_search
from src.utils.logger import get_logger
from src.utils.output_saver import SUPPORTED_OUTPUT_FORMATS, save_results

logger = get_logger(__name__)


def _check_venv() -> None:
    """Ensure the script is running inside a virtual environment."""
    if sys.prefix == sys.base_prefix:
        print("ERROR: Kallisto-OSINTer must be run inside a virtual environment!", file=sys.stderr)
        print("\nTo create and activate a virtual environment:", file=sys.stderr)
        print("  python -m venv venv", file=sys.stderr)
        print("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate", file=sys.stderr)
        print("  pip install -e .", file=sys.stderr)
        sys.exit(1)


def _add_output_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--output",
        type=str,
        help="Optional path to persist command results.",
    )
    parser.add_argument(
        "--output-format",
        choices=sorted(SUPPORTED_OUTPUT_FORMATS),
        help="Force an output format when saving results.",
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Kallisto-OSINTer: LLM-based OSINT tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    lookup_parser = subparsers.add_parser("person_lookup", help="Lookup a person")
    lookup_parser.add_argument("name", type=str, help="Name of the person to lookup")
    lookup_parser.add_argument("--ask", type=str, required=True, help="Task to perform on the person info")
    lookup_parser.add_argument("--location", type=str, help="Location to disambiguate person (e.g., 'San Francisco, CA')")
    _add_output_arguments(lookup_parser)

    uname_parser = subparsers.add_parser("username_search", help="Search for a username across URLs")
    uname_parser.add_argument("username", type=str, help="Username to search")
    uname_parser.add_argument("--urls", type=str, nargs='+', required=True, help="List of URLs to search in")
    _add_output_arguments(uname_parser)

    return parser.parse_args()


def _resolve_output_format(path: str, explicit_format: str | None) -> str:
    if explicit_format:
        return explicit_format
    return suffix if (suffix := Path(path).suffix.lstrip(".")) else "txt"


def _maybe_save_results(data: Any, output_path: str | None, output_format: str | None) -> None:
    if not output_path:
        return
    fmt = _resolve_output_format(output_path, output_format)
    try:
        saved_path = save_results(data, output_path, fmt)
        print(f"Results saved to {saved_path}")
    except ValueError as exc:
        logger.error("Failed to save results: %s", exc)
        print(f"Error: Failed to save results to {output_path}: {exc}")


def main() -> None:
    _check_venv()
    config = load_config()
    args = parse_arguments()

    if args.command == "person_lookup":
        logger.info("Starting person lookup for %s", args.name)
        result = person_lookup.lookup_person(args.name, args.ask, config, location=args.location)
        print(result)
        _maybe_save_results(result, args.output, args.output_format)
    elif args.command == "username_search":
        logger.info("Starting username search for %s", args.username)
        results = username_search.search_username(args.username, args.urls, config)
        for res in results:
            print(f"URL: {res['url']}, Status: {res['status']}")
        _maybe_save_results(results, args.output, args.output_format)
    else:  # pragma: no cover - argparse enforces valid commands
        logger.error("Unknown command: %s", args.command)
        sys.exit(1)


if __name__ == "__main__":
    main()
