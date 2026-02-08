# Implementation Plan: Spurs Survey Automation

## Overview

Build a Python CLI application that automates post-match rating surveys for r/coys. Implementation proceeds bottom-up: data models first, then each component (match data fetcher, survey generator, results compiler, infographic generator, results archive), wired together via CLI commands.

## Tasks

- [x] 1. Set up project structure and data models
  - [x] 1.1 Create project skeleton with directory structure, `pyproject.toml`, and dependencies (requests, pillow, thefuzz, hypothesis, pytest, google-api-python-client, numpy)
    - Create `src/spurs_survey/` package with `__init__.py`
    - Create `src/spurs_survey/models.py` with all dataclasses: `PlayerInfo`, `SubstitutionEvent`, `MatchData`, `RatingStats`, `PlayerRating`, `CompiledResults`, `MatchMetadata`, `CoachRatings`
    - Create `src/spurs_survey/formations.py` with `FORMATION_LAYOUTS` dict mapping formation strings to row configurations
    - Create `tests/` directory with `conftest.py`
    - _Requirements: 1.1, 3.6, 4.3_

  - [x] 1.2 Implement JSON serialization and deserialization for all data models
    - Add `to_dict()` and `from_dict()` class methods to each dataclass
    - Implement `save_results(results: CompiledResults, path: str)` and `load_results(path: str) -> CompiledResults` in `src/spurs_survey/storage.py`
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 1.3 Write property test for JSON round-trip (Property 8)
    - **Property 8: JSON Serialization Round-Trip**
    - Create Hypothesis strategies for generating random `CompiledResults` objects
    - Verify `from_dict(to_dict(obj))` equals original for all generated objects
    - **Validates: Requirements 6.1, 6.2, 6.3**

  - [x] 1.4 Write property test for formation layout (Property 10)
    - **Property 10: Formation Layout Produces Correct Player Count**
    - For each formation in `FORMATION_LAYOUTS`, verify row player counts sum to 11
    - **Validates: Requirements 4.3**

- [x] 2. Implement Match Data Fetcher
  - [x] 2.1 Implement football-data.org API client in `src/spurs_survey/match_data.py`
    - Implement `fetch_match_data(match_id: int) -> MatchData` that calls the API and parses the response into a `MatchData` object
    - Parse lineup (11 starters), formation, coach, substitutions, and match metadata from the API response
    - Handle API authentication via environment variable `FOOTBALL_DATA_API_KEY`
    - _Requirements: 1.1, 1.3, 1.5_

  - [x] 2.2 Implement player image fuzzy matching in `src/spurs_survey/match_data.py`
    - Implement `map_player_images(players: list[str], image_dir: str) -> dict[str, str | None]`
    - Use `thefuzz.fuzz.ratio` with a configurable threshold (default 70) to match API player names to local image filenames
    - Return `None` for players below the threshold
    - _Requirements: 1.2_

  - [x] 2.3 Implement fallback manual entry for missing data
    - Implement `prompt_missing_fields(match_data: MatchData) -> MatchData` that detects None/empty fields and prompts via stdin
    - Implement `detect_missing_fields(data: dict) -> list[str]` that returns the list of missing required field names
    - _Requirements: 1.4_

  - [x] 2.4 Write property tests for match data fetcher (Properties 1, 2, 3)
    - **Property 1: API Response Parsing Extracts All Required Fields**
    - **Property 2: Player Image Fuzzy Matching Returns Valid Results**
    - **Property 3: Missing Field Detection Is Complete**
    - Create Hypothesis strategies for random API response payloads, player name/filename pairs, and partial data dicts
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

- [x] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement Survey Generator
  - [x] 4.1 Implement Google Forms survey creation in `src/spurs_survey/survey.py`
    - Implement `create_survey(match_data: MatchData) -> str` that builds the form structure and returns the shareable link
    - Build form with sections in order: rating scale description header, team rating, opponent rating, coach ratings (3 questions), referee rating, starting player ratings, substitute player ratings (if any), MOTM vote
    - Use Google Forms API v1 with service account credentials from a JSON key file
    - Implement `build_survey_structure(match_data: MatchData) -> list[dict]` as a pure function that returns the form section definitions (testable without API)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 4.2 Write property tests for survey structure (Properties 4, 5)
    - **Property 4: Survey Structure and Section Ordering**
    - **Property 5: Man of the Match Options Completeness**
    - Test `build_survey_structure()` with random MatchData objects
    - Verify section order, rating scale, and MOTM options completeness
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

- [x] 5. Implement Results Compiler
  - [x] 5.1 Implement survey response compilation in `src/spurs_survey/results.py`
    - Implement `compile_responses(responses: list[dict], match_data: MatchData) -> CompiledResults`
    - Compute mean and standard deviation for each rated entity using numpy
    - Compute overall rating as mean of all player rating means
    - Determine MOTM winner(s) — player(s) with max vote count, handling ties
    - Record total response count
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [x] 5.2 Implement Google Forms response fetching in `src/spurs_survey/survey.py`
    - Implement `fetch_responses(form_id: str) -> list[dict]` that retrieves all responses from a Google Form
    - Parse response rows into a list of dicts keyed by question title
    - _Requirements: 3.1_

  - [x] 5.3 Write property tests for results compilation (Properties 6, 7)
    - **Property 6: Statistics Computation Correctness**
    - **Property 7: Man of the Match Winner Determination**
    - Generate random rating lists and vote lists, verify mean/stddev/MOTM computation
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement Infographic Generator
  - [x] 7.1 Implement infographic rendering in `src/spurs_survey/infographic.py`
    - Implement `generate_infographic(results: CompiledResults, quote: str, photo_path: str, output_path: str) -> str`
    - Create 1920x1080 canvas (16:9)
    - Render three-column layout: left sidebar (22%), main content (56%), right sidebar (22%)
    - Left sidebar: navy background, match header, score block, diamond overall rating, manager card with tactical ratings, photo of match area, quote of match text
    - Main content: blurred stadium background with blue overlay, formation-based player layout, referee rating, response count, legend
    - Right sidebar: substitute player cards in vertical list
    - Player cards: player image, uppercase black pill nameplate, yellow rating circle, gray stddev text, event badges
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.10_

  - [x] 7.2 Implement placeholder image handling
    - Create a silhouette placeholder PNG at `assets/placeholder.png`
    - When `image_path` is None or file not found, use the placeholder
    - _Requirements: 4.9_

  - [x] 7.3 Write property tests for infographic (Properties 9, 10, 11)
    - **Property 9: Infographic Output Dimensions**
    - **Property 10: (already covered in 1.4, skip here)**
    - **Property 11: Missing Player Images Do Not Cause Failures**
    - Generate random CompiledResults with some None image paths, verify valid PNG output with correct dimensions
    - **Validates: Requirements 4.1, 4.3, 4.9**

- [x] 8. Implement Results Archive Static Site
  - [x] 8.1 Create static site files in `archive/`
    - Create `archive/index.html` — match list page with filter controls (opponent, competition, date range) and match cards linking to individual results
    - Create `archive/match.html` — individual match page displaying the infographic image, loaded via query parameter
    - Create `archive/js/app.js` — client-side JS that fetches `data/matches.json`, renders match list, implements filtering and sorting (most recent first)
    - Create `archive/css/style.css` — styling for the archive pages
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 8.2 Implement site builder in `src/spurs_survey/archive.py`
    - Implement `build_site(data_dir: str, output_dir: str)` that reads all match result JSON files and generates `matches.json` index
    - Copy infographic PNGs to `archive/matches/<match_id>/`
    - Copy result JSON files to `archive/matches/<match_id>/`
    - _Requirements: 5.1, 5.5_

  - [x] 8.3 Write property tests for archive (Properties 12, 13)
    - **Property 12: Archive Match Sorting**
    - **Property 13: Archive Filtering Correctness**
    - Generate random match lists, verify sorting and filtering logic
    - **Validates: Requirements 5.1, 5.3**

- [x] 9. Wire CLI entry point
  - [x] 9.1 Implement CLI in `src/spurs_survey/cli.py`
    - Use `argparse` to create subcommands: `fetch`, `create-survey`, `compile`, `infographic`, `build-site`, `run`
    - `fetch <match_id>` — calls `fetch_match_data()`, saves to `data/matches/<match_id>/match_data.json`
    - `create-survey <match_id>` — loads match data, calls `create_survey()`, prints shareable link
    - `compile <match_id>` — fetches responses, calls `compile_responses()`, saves results JSON
    - `infographic <match_id> --quote "..." --photo path` — loads results, generates infographic PNG
    - `build-site` — rebuilds the static archive site
    - `run <match_id>` — runs full pipeline in sequence (fetch → create-survey → wait for user → compile → infographic → build-site)
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1_

  - [x] 9.2 Add `__main__.py` entry point
    - Create `src/spurs_survey/__main__.py` so the tool can be run via `python -m spurs_survey`
    - _Requirements: all_

- [x] 10. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases using pytest
- The Google Forms API requires a service account key file — the user will need to set this up via Google Cloud Console (free tier)
- The football-data.org API requires a free API key — register at football-data.org
