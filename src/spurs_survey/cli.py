"""CLI entry point for the Spurs Survey automation tool.

Subcommands:
  fetch <match_id>          Fetch match data from ESPN API
  create-survey <match_id>  Generate a Google Form from match data
  compile <match_id>        Compile survey responses into results
  infographic <match_id>    Generate results infographic PNG
  build-site                Rebuild the static results archive
  run <match_id>            Run the full pipeline end-to-end
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys

from spurs_survey.match_data import (
    fetch_match_data,
    map_player_images,
    prompt_missing_fields,
)
from spurs_survey.storage import load_results, save_results

logger = logging.getLogger(__name__)

# Default directories
DATA_DIR = "data/matches"
IMAGE_DIR = "tottenham 2025 squad/cropped images"
ARCHIVE_DIR = "archive"


def _match_data_path(match_id: str) -> str:
    return os.path.join(DATA_DIR, match_id, "match_data.json")


def _results_path(match_id: str) -> str:
    return os.path.join(DATA_DIR, match_id, "results.json")


def _infographic_path(match_id: str) -> str:
    return os.path.join(DATA_DIR, match_id, "infographic.png")


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def cmd_fetch(args: argparse.Namespace) -> None:
    """Fetch match data from the ESPN API and save to JSON."""
    from spurs_survey.models import MatchData

    match_id = args.match_id
    print(f"Fetching match data for event {match_id}...")

    match_data = fetch_match_data(int(match_id))

    # Map player images
    image_map = map_player_images(
        [p.name for p in match_data.starting_players],
        IMAGE_DIR,
    )
    for player in match_data.starting_players:
        mapped = image_map.get(player.name)
        if mapped:
            player.image_path = os.path.join(IMAGE_DIR, mapped)

    # Prompt for any missing fields
    match_data = prompt_missing_fields(match_data)

    # Save
    out_path = _match_data_path(match_id)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(match_data.to_dict(), f, indent=2, ensure_ascii=False)

    print(f"Match data saved to {out_path}")


def cmd_create_survey(args: argparse.Namespace) -> None:
    """Load match data and create a Google Form survey."""
    from spurs_survey.models import MatchData
    from spurs_survey.survey import create_survey

    match_id = args.match_id
    md_path = _match_data_path(match_id)

    if not os.path.isfile(md_path):
        print(f"Error: match data not found at {md_path}. Run 'fetch' first.", file=sys.stderr)
        sys.exit(1)

    with open(md_path, encoding="utf-8") as f:
        match_data = MatchData.from_dict(json.load(f))

    print("Creating Google Form survey...")
    link = create_survey(match_data)
    print(f"Survey link: {link}")


def cmd_compile(args: argparse.Namespace) -> None:
    """Fetch survey responses and compile results."""
    from spurs_survey.models import MatchData
    from spurs_survey.results import compile_responses
    from spurs_survey.survey import fetch_responses

    match_id = args.match_id
    md_path = _match_data_path(match_id)

    if not os.path.isfile(md_path):
        print(f"Error: match data not found at {md_path}. Run 'fetch' first.", file=sys.stderr)
        sys.exit(1)

    with open(md_path, encoding="utf-8") as f:
        match_data = MatchData.from_dict(json.load(f))

    form_id = args.form_id
    if not form_id:
        print("Error: --form-id is required for compile.", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching responses for form {form_id}...")
    responses = fetch_responses(form_id)
    print(f"Got {len(responses)} responses.")

    results = compile_responses(responses, match_data)

    out_path = _results_path(match_id)
    save_results(results, out_path)
    print(f"Results saved to {out_path}")


def cmd_infographic(args: argparse.Namespace) -> None:
    """Generate a results infographic PNG."""
    from spurs_survey.infographic import generate_infographic

    match_id = args.match_id
    results_file = _results_path(match_id)

    if not os.path.isfile(results_file):
        print(f"Error: results not found at {results_file}. Run 'compile' first.", file=sys.stderr)
        sys.exit(1)

    results = load_results(results_file)
    quote = args.quote or ""
    photo = args.photo or ""
    out_path = _infographic_path(match_id)

    print("Generating infographic...")
    generate_infographic(results, quote, photo, out_path)
    print(f"Infographic saved to {out_path}")


def cmd_build_site(args: argparse.Namespace) -> None:
    """Rebuild the static results archive."""
    from spurs_survey.archive import build_site

    print("Building archive site...")
    build_site(DATA_DIR, ARCHIVE_DIR)
    print("Archive site built.")


def cmd_run(args: argparse.Namespace) -> None:
    """Run the full pipeline: fetch → create-survey → wait → compile → infographic → build-site."""
    match_id = args.match_id

    # Step 1: Fetch
    fetch_ns = argparse.Namespace(match_id=match_id)
    cmd_fetch(fetch_ns)

    # Step 2: Create survey
    create_ns = argparse.Namespace(match_id=match_id)
    cmd_create_survey(create_ns)

    # Step 3: Wait for user to collect responses
    print("\nSurvey created. Collect responses, then press Enter to continue...")
    input()

    # Step 4: Compile — need form_id from user
    form_id = input("Enter the Google Form ID: ").strip()
    compile_ns = argparse.Namespace(match_id=match_id, form_id=form_id)
    cmd_compile(compile_ns)

    # Step 5: Infographic
    quote = input("Enter quote of the match (or press Enter to skip): ").strip()
    photo = input("Enter path to photo of the match (or press Enter to skip): ").strip()
    infographic_ns = argparse.Namespace(match_id=match_id, quote=quote, photo=photo)
    cmd_infographic(infographic_ns)

    # Step 6: Build site
    build_ns = argparse.Namespace()
    cmd_build_site(build_ns)

    print("\nPipeline complete!")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="spurs-survey",
        description="Automated post-match rating surveys for r/coys",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    subs = parser.add_subparsers(dest="command", help="Available commands")

    # fetch
    p_fetch = subs.add_parser("fetch", help="Fetch match data from ESPN API")
    p_fetch.add_argument("match_id", help="ESPN event ID")

    # create-survey
    p_create = subs.add_parser("create-survey", help="Create a Google Form survey")
    p_create.add_argument("match_id", help="ESPN event ID")

    # compile
    p_compile = subs.add_parser("compile", help="Compile survey responses")
    p_compile.add_argument("match_id", help="ESPN event ID")
    p_compile.add_argument("--form-id", required=True, help="Google Form ID")

    # infographic
    p_info = subs.add_parser("infographic", help="Generate results infographic")
    p_info.add_argument("match_id", help="ESPN event ID")
    p_info.add_argument("--quote", default="", help="Quote of the match")
    p_info.add_argument("--photo", default="", help="Path to photo of the match")

    # build-site
    subs.add_parser("build-site", help="Rebuild the static archive site")

    # run
    p_run = subs.add_parser("run", help="Run full pipeline end-to-end")
    p_run.add_argument("match_id", help="ESPN event ID")

    return parser


def main() -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    dispatch = {
        "fetch": cmd_fetch,
        "create-survey": cmd_create_survey,
        "compile": cmd_compile,
        "infographic": cmd_infographic,
        "build-site": cmd_build_site,
        "run": cmd_run,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    handler(args)


if __name__ == "__main__":
    main()
