"""CLI with optional YAML configuration file support.

This module provides the command-line interface for the BGG Extractor.
It supports configuration via CLI arguments or a YAML file, and executes
data extraction tasks using the high-level synchronous API.
"""

import argparse
import os
import sys
from typing import Any

import yaml
from dotenv import load_dotenv

from bgg_extractor import (
    get_collection,
    get_family,
    get_plays,
    get_things,
    get_user,
    save_csv,
    save_json,
    search,
)

load_dotenv()


def load_config(path: str) -> dict[str, Any]:
    """Load configuration from a YAML file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        A dictionary containing the configuration.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    Returns:
        An argparse.ArgumentParser instance.
    """
    p = argparse.ArgumentParser("bgg-extractor", description="Extract data from BoardGameGeek XML API2.")
    p.add_argument("--config", type=str, help="YAML config file (overrides CLI defaults, but CLI args override config)")
    p.add_argument(
        "--extractor", choices=["things", "collection", "user", "plays", "search", "family"], help="What to extract"
    )
    p.add_argument("--things", nargs="*", type=int, help="List of thing (game) IDs")
    p.add_argument("--families", nargs="*", type=int, help="List of family IDs")
    p.add_argument("--query", type=str, help="Search query")
    p.add_argument("--user", type=str, help="Username for collection/user/plays extraction")
    p.add_argument("--out", type=str, default="output.json", help="Output filename")
    p.add_argument("--format", choices=["csv", "json"], default="json", help="Output format")

    return p


def run_extraction(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """Run the extraction process based on arguments and configuration.

    Args:
        args: Parsed command-line arguments.
        cfg: Configuration dictionary loaded from YAML (if any).
    """
    extractor = args.extractor or cfg.get("extractor")
    things = args.things or cfg.get("things")
    families = args.families or cfg.get("families")
    query = args.query or cfg.get("query")
    username = args.user or cfg.get("user")
    out = args.out or cfg.get("out", "output.json")
    fmt = args.format or cfg.get("format", "json")

    # Token check is handled by the client, but we can fail early if needed.
    # However, the client raises ValueError, which is fine.

    data = None

    try:
        if extractor == "things":
            if not things:
                print("Error: --things (or config 'things') required for extractor=things", file=sys.stderr)
                sys.exit(1)
            print(f"Extracting things: {things}")
            schema = get_things(
                things, stats=True, versions=True, videos=True, marketplace=True, comments=True, ratingcomments=True
            )
            data = schema.items

        elif extractor == "family":
            if not families:
                print("Error: --families (or config 'families') required for extractor=family", file=sys.stderr)
                sys.exit(1)
            print(f"Extracting families: {families}")
            schema = get_family(families)
            data = schema.items

        elif extractor == "search":
            if not query:
                print("Error: --query (or config 'query') required for extractor=search", file=sys.stderr)
                sys.exit(1)
            print(f"Searching for: {query}")
            schema = search(query)
            data = schema.items

        elif extractor == "collection":
            if not username:
                print("Error: --user (or config 'user') required for extractor=collection", file=sys.stderr)
                sys.exit(1)
            print(f"Extracting collection for user: {username}")
            schema = get_collection(username, version=True, stats=True, showprivate=True)
            data = schema.items

        elif extractor == "user":
            if not username:
                print("Error: --user (or config 'user') required for extractor=user", file=sys.stderr)
                sys.exit(1)
            print(f"Extracting user profile: {username}")
            schema = get_user(username, buddies=True, guilds=True, hot=True, top=True)
            data = schema

        elif extractor == "plays":
            if not username:
                print("Error: --user (or config 'user') required for extractor=plays", file=sys.stderr)
                sys.exit(1)
            print(f"Extracting plays for user: {username}")
            schema = get_plays(username=username)
            data = schema.plays

        else:
            print("Error: No valid extractor specified. Use --extractor or config.", file=sys.stderr)
            sys.exit(1)

        # Save data
        if data:
            print(f"Saving to {out}...")
            if fmt == "json":
                save_json(data, out)
            elif fmt == "csv":
                if isinstance(data, list):
                    save_csv(data, out)
                else:
                    # Single object (like UserSchema) - wrap in list for CSV
                    save_csv([data], out)
            print("Done.")
        else:
            print("No data found.")

    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


def main(argv=None) -> None:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = {}
    if args.config:
        try:
            cfg = load_config(args.config)
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        run_extraction(args, cfg)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
