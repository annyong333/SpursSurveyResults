"""Persistence helpers for compiled match results."""

from __future__ import annotations

import json
import os
from pathlib import Path

from spurs_survey.models import CompiledResults


def save_results(results: CompiledResults, path: str) -> None:
    """Serialize *results* to a JSON file at *path*."""
    os.makedirs(Path(path).parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results.to_dict(), f, indent=2, ensure_ascii=False)


def load_results(path: str) -> CompiledResults:
    """Deserialize a JSON file at *path* into a CompiledResults object."""
    with open(path, encoding="utf-8") as f:
        return CompiledResults.from_dict(json.load(f))
