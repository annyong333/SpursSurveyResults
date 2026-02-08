"""Unit tests for the match data fetcher module (ESPN API)."""

from __future__ import annotations

from pathlib import Path

import pytest

from spurs_survey.match_data import (
    _parse_espn_response,
    _parse_minute,
    _short_position,
    detect_missing_fields,
    map_player_images,
)


# ---------------------------------------------------------------------------
# Position mapping
# ---------------------------------------------------------------------------

class TestShortPosition:
    def test_known_positions(self):
        assert _short_position("G") == "GK"
        assert _short_position("CD") == "CB"
        assert _short_position("LF") == "LW"
        assert _short_position("F") == "FW"

    def test_none_falls_back(self):
        assert _short_position(None) == "MF"

    def test_unknown_falls_back(self):
        assert _short_position("SW") == "MF"


# ---------------------------------------------------------------------------
# Minute parsing
# ---------------------------------------------------------------------------

class TestParseMinute:
    def test_simple(self):
        assert _parse_minute("32'") == 32

    def test_stoppage_time(self):
        assert _parse_minute("90'+2'") == 92

    def test_empty(self):
        assert _parse_minute("") == 0

    def test_no_quotes(self):
        assert _parse_minute("45") == 45


# ---------------------------------------------------------------------------
# ESPN response parsing
# ---------------------------------------------------------------------------

def _make_espn_response(
    *,
    spurs_home: bool = True,
    num_starters: int = 11,
    num_subs: int = 2,
) -> dict:
    """Build a minimal ESPN-style match summary response."""
    spurs_roster = [
        {
            "active": True,
            "starter": i < num_starters,
            "jersey": str(i + 1),
            "athlete": {
                "id": str(100 + i),
                "displayName": f"Player {i + 1}",
            },
            "position": {
                "abbreviation": "G" if i == 0 else "CD",
            },
            "subbedIn": i >= num_starters,
            "subbedOut": False,
            "formationPlace": str(i + 1),
        }
        for i in range(num_starters + 3)  # starters + bench
    ]

    opp_roster = [
        {
            "active": True,
            "starter": True,
            "jersey": str(i + 1),
            "athlete": {"id": str(200 + i), "displayName": f"Opp {i + 1}"},
            "position": {"abbreviation": "CD"},
            "subbedIn": False,
            "subbedOut": False,
        }
        for i in range(11)
    ]

    spurs_team = {"id": "367", "displayName": "Tottenham Hotspur"}
    opp_team = {"id": "360", "displayName": "Manchester United"}

    home_team = spurs_team if spurs_home else opp_team
    away_team = opp_team if spurs_home else spurs_team

    sub_events = [
        {
            "type": {"text": "Substitution"},
            "team": {"id": "367"},
            "clock": {"displayValue": f"{60 + i}'"},
            "participants": [
                {"athlete": {"displayName": f"Sub {i + 1}"}},
                {"athlete": {"displayName": f"Player {i + 1}"}},
            ],
        }
        for i in range(num_subs)
    ]

    return {
        "header": {
            "competitions": [
                {
                    "date": "2026-02-07T12:30:00Z",
                    "competitors": [
                        {
                            "homeAway": "home",
                            "team": home_team,
                            "score": "2",
                        },
                        {
                            "homeAway": "away",
                            "team": away_team,
                            "score": "0",
                        },
                    ],
                }
            ],
            "league": {"name": "English Premier League"},
            "season": {"type": 25},
        },
        "gameInfo": {"venue": {"fullName": "Old Trafford"}},
        "rosters": [
            {"team": home_team, "roster": spurs_roster if spurs_home else opp_roster},
            {"team": away_team, "roster": opp_roster if spurs_home else spurs_roster},
        ],
        "keyEvents": sub_events,
        "boxscore": {"form": [], "teams": []},
    }


class TestParseEspnResponse:
    def test_basic_parsing(self):
        resp = _make_espn_response()
        md = _parse_espn_response(resp, 740843)

        assert md.match_id == 740843
        assert md.home_team == "Tottenham Hotspur"
        assert md.away_team == "Manchester United"
        assert md.competition == "English Premier League"
        assert md.date == "2026-02-07"
        assert md.venue == "Old Trafford"
        assert md.is_tottenham_home is True
        assert md.home_score == 2
        assert md.away_score == 0
        assert len(md.starting_players) == 11
        assert len(md.substitutions) == 2

    def test_away_match(self):
        resp = _make_espn_response(spurs_home=False)
        md = _parse_espn_response(resp, 740843)

        assert md.is_tottenham_home is False
        assert md.home_team == "Manchester United"
        assert md.away_team == "Tottenham Hotspur"
        assert len(md.starting_players) == 11

    def test_no_substitutions(self):
        resp = _make_espn_response(num_subs=0)
        md = _parse_espn_response(resp, 740843)
        assert md.substitutions == []

    def test_non_spurs_match_raises(self):
        resp = _make_espn_response()
        # Change both team IDs to non-Spurs
        for c in resp["header"]["competitions"][0]["competitors"]:
            c["team"]["id"] = "999"
        with pytest.raises(ValueError, match="Tottenham"):
            _parse_espn_response(resp, 740843)

    def test_substitution_details(self):
        resp = _make_espn_response(num_subs=1)
        md = _parse_espn_response(resp, 740843)
        sub = md.substitutions[0]
        assert sub.player_in == "Sub 1"
        assert sub.player_out == "Player 1"
        assert sub.minute == 60

    def test_player_positions(self):
        resp = _make_espn_response()
        md = _parse_espn_response(resp, 740843)
        assert md.starting_players[0].position == "GK"  # first player is G
        assert md.starting_players[1].position == "CB"  # rest are CD


# ---------------------------------------------------------------------------
# Fuzzy image matching
# ---------------------------------------------------------------------------

class TestMapPlayerImages:
    def test_exact_match(self, tmp_path: Path):
        (tmp_path / "son_heungmin.png").touch()
        result = map_player_images(["son heungmin"], str(tmp_path))
        assert result["son heungmin"] == "son_heungmin.png"

    def test_fuzzy_match(self, tmp_path: Path):
        (tmp_path / "james_maddison.png").touch()
        result = map_player_images(["James Maddison"], str(tmp_path))
        assert result["James Maddison"] == "james_maddison.png"

    def test_below_threshold_returns_none(self, tmp_path: Path):
        (tmp_path / "completely_different.png").touch()
        result = map_player_images(["Son Heung-min"], str(tmp_path), threshold=70)
        assert result["Son Heung-min"] is None

    def test_nonexistent_dir(self):
        result = map_player_images(["Player"], "/nonexistent/dir")
        assert result["Player"] is None

    def test_empty_player_list(self, tmp_path: Path):
        result = map_player_images([], str(tmp_path))
        assert result == {}

    def test_multiple_players(self, tmp_path: Path):
        (tmp_path / "james_maddison.png").touch()
        (tmp_path / "dejan_kulusevski.png").touch()
        result = map_player_images(
            ["James Maddison", "Dejan Kulusevski"],
            str(tmp_path),
        )
        assert result["James Maddison"] == "james_maddison.png"
        assert result["Dejan Kulusevski"] == "dejan_kulusevski.png"


# ---------------------------------------------------------------------------
# Missing field detection
# ---------------------------------------------------------------------------

class TestDetectMissingFields:
    def test_complete_data(self):
        data = {
            "home_team": "Spurs",
            "away_team": "Newcastle",
            "competition": "PL",
            "matchday": "Week 3",
            "date": "2024-09-01",
            "venue": "Stadium",
            "formation": "4-3-3",
            "coach": "Ange",
            "starting_players": [{"name": "P1"}],
        }
        assert detect_missing_fields(data) == []

    def test_empty_strings_detected(self):
        data = {
            "home_team": "",
            "away_team": "Newcastle",
            "competition": "PL",
            "matchday": "Week 3",
            "date": "2024-09-01",
            "venue": "Stadium",
            "formation": "4-3-3",
            "coach": "Ange",
            "starting_players": [{"name": "P1"}],
        }
        assert "home_team" in detect_missing_fields(data)

    def test_none_values_detected(self):
        data = {
            "home_team": "Spurs",
            "away_team": "Newcastle",
            "competition": None,
            "matchday": "Week 3",
            "date": "2024-09-01",
            "venue": "Stadium",
            "formation": "4-3-3",
            "coach": "Ange",
            "starting_players": [{"name": "P1"}],
        }
        assert "competition" in detect_missing_fields(data)

    def test_missing_players_detected(self):
        data = {
            "home_team": "Spurs",
            "away_team": "Newcastle",
            "competition": "PL",
            "matchday": "Week 3",
            "date": "2024-09-01",
            "venue": "Stadium",
            "formation": "4-3-3",
            "coach": "Ange",
            "starting_players": [],
        }
        assert "starting_players" in detect_missing_fields(data)

    def test_multiple_missing(self):
        data = {}
        missing = detect_missing_fields(data)
        assert len(missing) == 9  # 8 required fields + starting_players


# ---------------------------------------------------------------------------
# Hypothesis strategies and property-based tests (Properties 1, 2, 3)
# ---------------------------------------------------------------------------

from hypothesis import given, settings
from hypothesis import strategies as st

from spurs_survey.models import MatchData, PlayerInfo, SubstitutionEvent


# -- Strategies for ESPN-like API responses --------------------------------

_POSITIONS = ["G", "CD", "CD-L", "CD-R", "LB", "RB", "DM", "CM", "AM", "LM", "RM", "LW", "RW", "F", "CF"]

def _espn_roster_entry(index: int, *, starter: bool) -> dict:
    """Build a single ESPN roster entry."""
    return {
        "active": True,
        "starter": starter,
        "jersey": str(index + 1),
        "athlete": {"id": str(100 + index), "displayName": f"Player {index + 1}"},
        "position": {"abbreviation": _POSITIONS[index % len(_POSITIONS)]},
        "subbedIn": not starter,
        "subbedOut": False,
        "formationPlace": str(index + 1),
    }


@st.composite
def espn_response_strategy(draw):
    """Generate a valid ESPN-style match summary response with Spurs."""
    spurs_home = draw(st.booleans())
    num_subs = draw(st.integers(min_value=0, max_value=5))
    home_score = draw(st.integers(min_value=0, max_value=9))
    away_score = draw(st.integers(min_value=0, max_value=9))
    competition_name = draw(st.text(min_size=1, max_size=30, alphabet=st.characters(categories=("L", "N", "Z"))))
    date_str = draw(st.dates().map(lambda d: d.isoformat() + "T12:00:00Z"))
    venue_name = draw(st.text(min_size=1, max_size=40, alphabet=st.characters(categories=("L", "N", "Z"))))

    # Build 11 starters + 3 bench
    spurs_roster = [_espn_roster_entry(i, starter=(i < 11)) for i in range(14)]
    opp_roster = [
        {
            "active": True, "starter": True, "jersey": str(i + 1),
            "athlete": {"id": str(200 + i), "displayName": f"Opp {i + 1}"},
            "position": {"abbreviation": "CD"},
            "subbedIn": False, "subbedOut": False,
        }
        for i in range(11)
    ]

    spurs_team = {"id": "367", "displayName": "Tottenham Hotspur"}
    opp_team = {"id": "360", "displayName": "Opponent FC"}

    home_team = spurs_team if spurs_home else opp_team
    away_team = opp_team if spurs_home else spurs_team

    sub_events = [
        {
            "type": {"text": "Substitution"},
            "team": {"id": "367"},
            "clock": {"displayValue": f"{60 + i}'"},
            "participants": [
                {"athlete": {"displayName": f"Sub {i + 1}"}},
                {"athlete": {"displayName": f"Player {i + 1}"}},
            ],
        }
        for i in range(num_subs)
    ]

    resp = {
        "header": {
            "competitions": [
                {
                    "date": date_str,
                    "competitors": [
                        {"homeAway": "home", "team": home_team, "score": str(home_score)},
                        {"homeAway": "away", "team": away_team, "score": str(away_score)},
                    ],
                }
            ],
            "league": {"name": competition_name},
            "season": {"type": 25},
        },
        "gameInfo": {"venue": {"fullName": venue_name}},
        "rosters": [
            {"team": home_team, "roster": spurs_roster if spurs_home else opp_roster},
            {"team": away_team, "roster": opp_roster if spurs_home else spurs_roster},
        ],
        "keyEvents": sub_events,
        "boxscore": {"form": [], "teams": []},
    }
    return resp


# -- Property 1: API Response Parsing Extracts All Required Fields ---------

@given(resp=espn_response_strategy())
@settings(max_examples=100)
def test_property1_api_parsing_extracts_required_fields(resp: dict) -> None:
    """For any valid ESPN API response, parsing SHALL produce a MatchData with
    exactly 11 starters, a non-empty competition, and populated metadata.

    # Feature: spurs-survey-automation, Property 1: API Response Parsing Extracts All Required Fields
    **Validates: Requirements 1.1, 1.3, 1.5**
    """
    md = _parse_espn_response(resp, 99999)

    # Exactly 11 starting players
    assert len(md.starting_players) == 11

    # Competition is populated
    assert md.competition != ""

    # Date is populated
    assert md.date != ""

    # Venue is populated
    assert md.venue != ""

    # Team names are populated
    assert md.home_team != ""
    assert md.away_team != ""

    # Scores are integers
    assert isinstance(md.home_score, int)
    assert isinstance(md.away_score, int)


# -- Property 2: Player Image Fuzzy Matching Returns Valid Results ---------

@st.composite
def player_and_files_strategy(draw):
    """Generate a list of player names and a set of image filenames."""
    num_players = draw(st.integers(min_value=1, max_value=10))
    players = [draw(st.text(min_size=1, max_size=30, alphabet=st.characters(categories=("L",)))) for _ in range(num_players)]
    num_files = draw(st.integers(min_value=1, max_value=15))
    filenames = [draw(st.text(min_size=1, max_size=25, alphabet=st.characters(categories=("L",)))) + ".png" for _ in range(num_files)]
    threshold = draw(st.integers(min_value=0, max_value=100))
    return players, filenames, threshold


@given(data=player_and_files_strategy())
@settings(max_examples=100)
def test_property2_fuzzy_matching_returns_valid_results(data, tmp_path_factory) -> None:
    """For any player name and non-empty set of image filenames, the mapper
    SHALL return either a filename in the set or None.

    # Feature: spurs-survey-automation, Property 2: Player Image Fuzzy Matching Returns Valid Results
    **Validates: Requirements 1.2**
    """
    players, filenames, threshold = data

    # Create a temp directory with the image files
    tmp_dir = tmp_path_factory.mktemp("images")
    for fname in filenames:
        (tmp_dir / fname).touch()

    result = map_player_images(players, str(tmp_dir), threshold=threshold)

    # Every player must have an entry
    assert set(result.keys()) == set(players)

    # Collect actual files in the directory for validation
    actual_files = {f.name for f in tmp_dir.iterdir() if f.is_file()}

    for player_name, matched_file in result.items():
        if matched_file is not None:
            # The returned filename must exist in the directory
            assert matched_file in actual_files, (
                f"Returned '{matched_file}' for '{player_name}' but it's not in {actual_files}"
            )


# -- Property 3: Missing Field Detection Is Complete -----------------------

@st.composite
def partial_data_strategy(draw):
    """Generate a complete data dict then remove a random subset of required fields."""
    from spurs_survey.match_data import _REQUIRED_FIELDS

    # Start with a fully populated dict
    complete = {
        "home_team": draw(st.text(min_size=1, max_size=20, alphabet=st.characters(categories=("L",)))),
        "away_team": draw(st.text(min_size=1, max_size=20, alphabet=st.characters(categories=("L",)))),
        "competition": draw(st.text(min_size=1, max_size=20, alphabet=st.characters(categories=("L",)))),
        "matchday": draw(st.text(min_size=1, max_size=20, alphabet=st.characters(categories=("L",)))),
        "date": draw(st.text(min_size=1, max_size=20, alphabet=st.characters(categories=("L", "N")))),
        "venue": draw(st.text(min_size=1, max_size=20, alphabet=st.characters(categories=("L",)))),
        "formation": draw(st.text(min_size=1, max_size=10, alphabet=st.characters(categories=("L", "N", "P")))),
        "coach": draw(st.text(min_size=1, max_size=20, alphabet=st.characters(categories=("L",)))),
        "starting_players": [{"name": "P1"}],  # always at least one
    }

    # Choose a subset of fields to remove (including possibly "starting_players")
    all_removable = _REQUIRED_FIELDS + ["starting_players"]
    fields_to_remove = draw(
        st.lists(st.sampled_from(all_removable), unique=True, min_size=0, max_size=len(all_removable))
    )

    for field_name in fields_to_remove:
        if field_name == "starting_players":
            complete["starting_players"] = []  # empty = missing
        else:
            complete[field_name] = ""  # empty string = missing

    return complete, set(fields_to_remove)


@given(data=partial_data_strategy())
@settings(max_examples=100)
def test_property3_missing_field_detection_is_complete(data) -> None:
    """For any data dict with a subset of required fields removed, the detector
    SHALL report exactly the removed fields — no more, no fewer.

    # Feature: spurs-survey-automation, Property 3: Missing Field Detection Is Complete
    **Validates: Requirements 1.4**
    """
    data_dict, removed_fields = data
    detected = set(detect_missing_fields(data_dict))
    assert detected == removed_fields, (
        f"Expected missing={removed_fields}, got detected={detected}"
    )
