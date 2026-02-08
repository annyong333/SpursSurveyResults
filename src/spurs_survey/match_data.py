"""Match data fetcher — retrieves lineups, formations, and substitutions.

Uses ESPN's public soccer API (no key required) and fuzzy matching for
player images.
"""

from __future__ import annotations

import logging
import pathlib

import requests
from thefuzz import fuzz

from spurs_survey.models import MatchData, PlayerInfo, SubstitutionEvent

logger = logging.getLogger(__name__)

ESPN_API_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"
TOTTENHAM_ESPN_ID = "367"  # ESPN team ID for Tottenham Hotspur

# ESPN position abbreviations → our short codes.
_POSITION_MAP: dict[str, str] = {
    "G": "GK",
    "D": "CB",
    "CD": "CB",
    "CD-L": "CB",
    "CD-R": "CB",
    "LB": "LB",
    "RB": "RB",
    "DM": "DM",
    "CM": "CM",
    "AM": "AM",
    "LM": "LM",
    "RM": "RM",
    "LW": "LW",
    "RW": "RW",
    "LF": "LW",
    "RF": "RW",
    "F": "FW",
    "CF": "FW",
    "SS": "FW",
}


def _short_position(abbrev: str | None) -> str:
    """Convert an ESPN position abbreviation to our short code."""
    if abbrev is None:
        return "MF"
    return _POSITION_MAP.get(abbrev, "MF")


# ---------------------------------------------------------------------------
# ESPN league slug mapping
# ---------------------------------------------------------------------------

# Maps common competition names / codes to ESPN league slugs.
_LEAGUE_SLUGS: dict[str, str] = {
    "eng.1": "eng.1",
    "eng.2": "eng.2",
    "eng.fa": "eng.fa",
    "eng.league_cup": "eng.league_cup",
    "uefa.champions": "uefa.champions",
    "uefa.europa": "uefa.europa",
    "uefa.europa.conf": "uefa.europa.conf",
}

# Default to Premier League when searching by date.
DEFAULT_LEAGUE = "eng.1"


# ---------------------------------------------------------------------------
# API client
# ---------------------------------------------------------------------------

def fetch_match_data(
    espn_event_id: int | str,
    league: str = DEFAULT_LEAGUE,
) -> MatchData:
    """Fetch lineup, formation, subs, and metadata for a Tottenham match.

    Parameters
    ----------
    espn_event_id:
        The ESPN event/game ID (visible in ESPN match URLs).
    league:
        ESPN league slug, e.g. ``"eng.1"`` for Premier League.

    Raises
    ------
    ValueError
        If Tottenham is not one of the teams in the match.
    requests.HTTPError
        If the ESPN API request fails.
    """
    url = f"{ESPN_API_BASE}/{league}/summary"
    resp = requests.get(url, params={"event": str(espn_event_id)}, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    return _parse_espn_response(data, int(espn_event_id))


def find_spurs_match(
    date: str,
    league: str = DEFAULT_LEAGUE,
) -> int | None:
    """Find the ESPN event ID for a Spurs match on a given date.

    Parameters
    ----------
    date:
        ISO date string, e.g. ``"2026-02-07"``.
    league:
        ESPN league slug.

    Returns
    -------
    The ESPN event ID, or ``None`` if no Spurs match found on that date.
    """
    url = f"{ESPN_API_BASE}/{league}/scoreboard"
    ymd = date.replace("-", "")
    resp = requests.get(url, params={"dates": ymd}, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    for event in data.get("events", []):
        for comp in event.get("competitions", []):
            for team in comp.get("competitors", []):
                if team.get("team", {}).get("id") == TOTTENHAM_ESPN_ID:
                    return int(event["id"])
    return None


# ---------------------------------------------------------------------------
# ESPN response parsing
# ---------------------------------------------------------------------------

def _parse_espn_response(data: dict, event_id: int) -> MatchData:
    """Parse an ESPN match summary response into a ``MatchData`` object."""
    header = data.get("header", {})
    competitions = header.get("competitions", [])
    if not competitions:
        raise ValueError("No competition data in ESPN response")
    comp = competitions[0]

    # Identify home / away teams
    competitors = comp.get("competitors", [])
    home_comp = next((c for c in competitors if c.get("homeAway") == "home"), {})
    away_comp = next((c for c in competitors if c.get("homeAway") == "away"), {})

    home_team_name = home_comp.get("team", {}).get("displayName", "")
    away_team_name = away_comp.get("team", {}).get("displayName", "")
    home_team_id = home_comp.get("team", {}).get("id", "")
    away_team_id = away_comp.get("team", {}).get("id", "")

    if home_team_id == TOTTENHAM_ESPN_ID:
        is_home = True
    elif away_team_id == TOTTENHAM_ESPN_ID:
        is_home = False
    else:
        raise ValueError(
            f"Tottenham (ESPN id={TOTTENHAM_ESPN_ID}) is not in this match. "
            f"Home: {home_team_name}, Away: {away_team_name}"
        )

    # Scores
    home_score = int(home_comp.get("score", 0))
    away_score = int(away_comp.get("score", 0))

    # Competition / league info
    league_info = header.get("league", {})
    competition_name = league_info.get("name", "")

    # Date
    utc_date = comp.get("date", "")
    date_str = utc_date[:10] if utc_date else ""

    # Venue
    game_info = data.get("gameInfo", {})
    venue = game_info.get("venue", {}).get("fullName", "")

    # Matchday — ESPN doesn't always provide this directly
    season = header.get("season", {})
    matchday = f"Matchday {season.get('type', '')}" if season else ""

    # ---------------------------------------------------------------
    # Rosters — find the Spurs roster
    # ---------------------------------------------------------------
    spurs_roster: list[dict] = []
    for team_roster in data.get("rosters", []):
        team_id = str(team_roster.get("team", {}).get("id", ""))
        if team_id == TOTTENHAM_ESPN_ID:
            spurs_roster = team_roster.get("roster", [])
            break

    # Starting players
    starting_players: list[PlayerInfo] = []
    for p in spurs_roster:
        if not p.get("starter"):
            continue
        athlete = p.get("athlete", {})
        pos_abbrev = p.get("position", {}).get("abbreviation")
        jersey = p.get("jersey")
        starting_players.append(
            PlayerInfo(
                name=athlete.get("displayName", ""),
                position=_short_position(pos_abbrev),
                shirt_number=int(jersey) if jersey else None,
            )
        )

    # ---------------------------------------------------------------
    # Substitutions — from keyEvents
    # ---------------------------------------------------------------
    substitutions: list[SubstitutionEvent] = []
    for ev in data.get("keyEvents", []):
        ev_type = ev.get("type", {}).get("text", "")
        if ev_type != "Substitution":
            continue
        ev_team_id = str(ev.get("team", {}).get("id", ""))
        if ev_team_id != TOTTENHAM_ESPN_ID:
            continue
        participants = ev.get("participants", [])
        if len(participants) < 2:
            continue
        player_in = participants[0].get("athlete", {}).get("displayName", "")
        player_out = participants[1].get("athlete", {}).get("displayName", "")
        clock_str = ev.get("clock", {}).get("displayValue", "0")
        minute = _parse_minute(clock_str)
        substitutions.append(
            SubstitutionEvent(player_in=player_in, player_out=player_out, minute=minute)
        )

    # ---------------------------------------------------------------
    # Formation — ESPN doesn't always provide a formation string.
    # We'll try to infer from formationPlace values, or leave blank
    # for the user to fill via prompt_missing_fields.
    # ---------------------------------------------------------------
    formation = ""
    # Check boxscore form data (sometimes present)
    for form_entry in data.get("boxscore", {}).get("form", []):
        form_team_id = str(form_entry.get("team", {}).get("id", ""))
        if form_team_id == TOTTENHAM_ESPN_ID:
            # ESPN occasionally includes formation in form data
            formation = form_entry.get("formation", "")
            break

    # Coach — ESPN doesn't include coach in the summary API.
    # This will be filled via prompt_missing_fields if needed.
    coach = ""

    return MatchData(
        match_id=event_id,
        home_team=home_team_name,
        away_team=away_team_name,
        competition=competition_name,
        matchday=matchday,
        date=date_str,
        venue=venue,
        formation=formation,
        coach=coach,
        starting_players=starting_players,
        substitutions=substitutions,
        is_tottenham_home=is_home,
        home_score=home_score,
        away_score=away_score,
    )


def _parse_minute(clock_str: str) -> int:
    """Parse an ESPN clock string like ``\"32'\"`` or ``\"90'+2'\"`` to an int."""
    clean = clock_str.replace("'", "").replace("'", "").strip()
    if "+" in clean:
        parts = clean.split("+")
        try:
            return int(parts[0]) + int(parts[1])
        except (ValueError, IndexError):
            return 0
    try:
        return int(clean)
    except ValueError:
        return 0


# ---------------------------------------------------------------------------
# Player image fuzzy matching
# ---------------------------------------------------------------------------

def map_player_images(
    players: list[str],
    image_dir: str,
    threshold: int = 70,
) -> dict[str, str | None]:
    """Map player names to local image filenames using fuzzy matching.

    Parameters
    ----------
    players:
        List of player names (as returned by the API).
    image_dir:
        Path to the directory containing player image files.
    threshold:
        Minimum ``thefuzz.fuzz.ratio`` score to accept a match (0–100).

    Returns
    -------
    dict mapping each player name to the best-matching filename (relative to
    *image_dir*), or ``None`` if no filename scores above *threshold*.
    """
    dir_path = pathlib.Path(image_dir)
    if not dir_path.is_dir():
        logger.warning("Image directory does not exist: %s", image_dir)
        return {name: None for name in players}

    # Collect image filenames (without extension) for matching
    image_files: list[str] = [
        f.name
        for f in dir_path.iterdir()
        if f.is_file() and f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    ]

    result: dict[str, str | None] = {}
    for player_name in players:
        best_score = 0
        best_file: str | None = None
        # Normalise the player name for comparison
        normalised_name = player_name.lower().replace("-", " ").replace("_", " ")
        for filename in image_files:
            stem = pathlib.Path(filename).stem.lower().replace("_", " ").replace("-", " ")
            score = fuzz.ratio(normalised_name, stem)
            if score > best_score:
                best_score = score
                best_file = filename
        result[player_name] = best_file if best_score >= threshold else None

    return result


# ---------------------------------------------------------------------------
# Missing-field detection and manual fallback
# ---------------------------------------------------------------------------

# Fields that must be non-empty / non-None for a valid MatchData.
_REQUIRED_FIELDS: list[str] = [
    "home_team",
    "away_team",
    "competition",
    "matchday",
    "date",
    "venue",
    "formation",
    "coach",
]


def detect_missing_fields(data: dict) -> list[str]:
    """Return the list of required field names that are missing or empty.

    A field is considered missing if its value is ``None``, an empty string,
    or an empty list.
    """
    missing: list[str] = []
    for field_name in _REQUIRED_FIELDS:
        value = data.get(field_name)
        if value is None or value == "" or value == []:
            missing.append(field_name)

    # Also check that we have at least some starting players
    players = data.get("starting_players", [])
    if not players:
        missing.append("starting_players")

    return missing


def prompt_missing_fields(match_data: MatchData) -> MatchData:
    """Interactively prompt the user to fill in missing/empty fields.

    Reads from stdin. Returns a new ``MatchData`` with the gaps filled.
    """
    data = match_data.to_dict()
    missing = detect_missing_fields(data)

    if not missing:
        return match_data

    print("\nThe following required fields are missing or empty:")
    for name in missing:
        print(f"  - {name}")
    print()

    for name in missing:
        if name == "starting_players":
            print("Starting players are missing. Please enter 11 player names, one per line.")
            print("Format: name,position (e.g., 'Son Heung-min,LW')")
            players: list[PlayerInfo] = []
            for i in range(11):
                while True:
                    raw = input(f"  Player {i + 1}: ").strip()
                    if "," in raw:
                        pname, pos = raw.split(",", 1)
                        players.append(PlayerInfo(name=pname.strip(), position=pos.strip()))
                        break
                    else:
                        print("    Please use format: name,position")
            data["starting_players"] = [p.to_dict() for p in players]
        else:
            value = input(f"  Enter value for '{name}': ").strip()
            data[name] = value

    return MatchData.from_dict(data)
