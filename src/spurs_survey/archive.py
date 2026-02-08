"""Site builder for the results archive.

Reads compiled match result JSON files from a data directory, generates a
``matches.json`` index, and copies result files and infographic PNGs into the
archive output directory.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from pathlib import Path

from spurs_survey.storage import load_results

logger = logging.getLogger(__name__)


def build_site(data_dir: str, output_dir: str) -> None:
    """Build the static archive site from match result data.

    Parameters
    ----------
    data_dir:
        Path to the directory containing per-match subdirectories.  Each
        subdirectory is expected to be named by match ID and contain at least
        a ``results.json`` file and optionally an ``infographic.png``.
    output_dir:
        Path to the archive output directory (e.g. ``archive/``).  The builder
        will create ``data/matches.json`` and ``matches/<id>/`` directories
        inside this folder.
    """

    data_path = Path(data_dir)
    out_path = Path(output_dir)

    matches_out = out_path / "matches"
    data_out = out_path / "data"
    os.makedirs(matches_out, exist_ok=True)
    os.makedirs(data_out, exist_ok=True)

    index_entries: list[dict] = []

    if not data_path.is_dir():
        logger.warning("Data directory %s does not exist — writing empty index.", data_dir)
        _write_index(data_out / "matches.json", [])
        return

    for match_dir in sorted(data_path.iterdir()):
        if not match_dir.is_dir():
            continue

        results_file = match_dir / "results.json"
        if not results_file.exists():
            logger.warning("Skipping %s — no results.json found.", match_dir.name)
            continue

        try:
            results = load_results(str(results_file))
        except Exception:
            logger.warning("Skipping %s — failed to load results.json.", match_dir.name, exc_info=True)
            continue

        match_id = str(results.match_id)
        dest = matches_out / match_id
        os.makedirs(dest, exist_ok=True)

        # Copy results JSON
        shutil.copy2(str(results_file), str(dest / "results.json"))

        # Copy infographic if present
        infographic = match_dir / "infographic.png"
        if infographic.exists():
            shutil.copy2(str(infographic), str(dest / "infographic.png"))

        meta = results.match_metadata
        index_entries.append({
            "match_id": results.match_id,
            "opponent": meta.opponent,
            "competition": meta.competition,
            "matchday": meta.matchday,
            "date": meta.date,
            "venue": meta.venue,
            "home_score": meta.home_score,
            "away_score": meta.away_score,
            "is_tottenham_home": meta.is_tottenham_home,
        })

    # Sort most recent first
    index_entries = sort_matches(index_entries)
    _write_index(data_out / "matches.json", index_entries)
    logger.info("Archive built: %d match(es) indexed.", len(index_entries))

def sort_matches(entries: list[dict]) -> list[dict]:
    """Return match entries sorted by date descending (most recent first)."""
    return sorted(entries, key=lambda m: m["date"], reverse=True)


def filter_matches(
    entries: list[dict],
    *,
    opponent: str | None = None,
    competition: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict]:
    """Filter match entries by optional criteria.

    Mirrors the client-side ``applyFilters`` logic in ``app.js``.
    """
    result = []
    for m in entries:
        if opponent and m["opponent"] != opponent:
            continue
        if competition and m["competition"] != competition:
            continue
        if date_from and m["date"] < date_from:
            continue
        if date_to and m["date"] > date_to:
            continue
        result.append(m)
    return result




def _write_index(path: Path, entries: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
