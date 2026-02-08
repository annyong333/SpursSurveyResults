"""Property-based tests for results compilation.

Feature: spurs-survey-automation, Property 6: Statistics Computation Correctness
Feature: spurs-survey-automation, Property 7: Man of the Match Winner Determination
Feature: spurs-survey-automation, Property 8: JSON Serialization Round-Trip
"""

from __future__ import annotations

import math

from hypothesis import given, settings
from hypothesis import strategies as st

from spurs_survey.models import (
    CoachRatings,
    CompiledResults,
    MatchMetadata,
    PlayerRating,
    RatingStats,
)


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

# Use finite floats only — JSON cannot represent NaN / Inf.
finite_floats = st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)

rating_stats_st = st.builds(
    RatingStats,
    mean=finite_floats,
    std_dev=finite_floats,
)

player_rating_st = st.builds(
    PlayerRating,
    name=st.text(min_size=1, max_size=30),
    position=st.sampled_from(["GK", "CB", "LB", "RB", "CM", "DM", "AM", "LW", "RW", "FW"]),
    image_path=st.one_of(st.none(), st.text(min_size=1, max_size=60)),
    rating=rating_stats_st,
    is_starter=st.booleans(),
    goals=st.integers(min_value=0, max_value=10),
    assists=st.integers(min_value=0, max_value=10),
    own_goals=st.integers(min_value=0, max_value=5),
    is_motm=st.booleans(),
)

match_metadata_st = st.builds(
    MatchMetadata,
    opponent=st.text(min_size=1, max_size=30),
    competition=st.text(min_size=1, max_size=30),
    matchday=st.text(min_size=1, max_size=20),
    date=st.text(min_size=1, max_size=20),
    venue=st.text(min_size=1, max_size=40),
    home_score=st.integers(min_value=0, max_value=15),
    away_score=st.integers(min_value=0, max_value=15),
    is_tottenham_home=st.booleans(),
)

coach_ratings_st = st.builds(
    CoachRatings,
    name=st.text(min_size=1, max_size=30),
    starting_eleven=rating_stats_st,
    on_field_tactics=rating_stats_st,
    substitutions=rating_stats_st,
)

formations = st.sampled_from(["4-3-3", "4-4-2", "3-5-2", "4-2-3-1", "3-4-3", "5-3-2", "4-1-4-1"])

compiled_results_st = st.builds(
    CompiledResults,
    match_id=st.integers(min_value=1, max_value=999999),
    match_metadata=match_metadata_st,
    team_rating=rating_stats_st,
    opponent_rating=rating_stats_st,
    referee_rating=rating_stats_st,
    coach_ratings=coach_ratings_st,
    overall_rating=finite_floats,
    starting_player_ratings=st.lists(player_rating_st, min_size=0, max_size=11),
    substitute_player_ratings=st.lists(player_rating_st, min_size=0, max_size=5),
    motm_winners=st.lists(st.text(min_size=1, max_size=30), min_size=0, max_size=3),
    total_responses=st.integers(min_value=0, max_value=10000),
    formation=formations,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _floats_equal(a: float, b: float) -> bool:
    """Compare floats accounting for JSON round-trip precision."""
    if a == b:
        return True
    return math.isclose(a, b, rel_tol=1e-9)


def _rating_stats_equal(a: RatingStats, b: RatingStats) -> bool:
    return _floats_equal(a.mean, b.mean) and _floats_equal(a.std_dev, b.std_dev)


def _player_rating_equal(a: PlayerRating, b: PlayerRating) -> bool:
    return (
        a.name == b.name
        and a.position == b.position
        and a.image_path == b.image_path
        and _rating_stats_equal(a.rating, b.rating)
        and a.is_starter == b.is_starter
        and a.goals == b.goals
        and a.assists == b.assists
        and a.own_goals == b.own_goals
        and a.is_motm == b.is_motm
    )


def _compiled_results_equal(a: CompiledResults, b: CompiledResults) -> bool:
    if a.match_id != b.match_id:
        return False
    if a.match_metadata != b.match_metadata:
        return False
    if not _rating_stats_equal(a.team_rating, b.team_rating):
        return False
    if not _rating_stats_equal(a.opponent_rating, b.opponent_rating):
        return False
    if not _rating_stats_equal(a.referee_rating, b.referee_rating):
        return False
    # Coach ratings
    cr_a, cr_b = a.coach_ratings, b.coach_ratings
    if cr_a.name != cr_b.name:
        return False
    if not _rating_stats_equal(cr_a.starting_eleven, cr_b.starting_eleven):
        return False
    if not _rating_stats_equal(cr_a.on_field_tactics, cr_b.on_field_tactics):
        return False
    if not _rating_stats_equal(cr_a.substitutions, cr_b.substitutions):
        return False
    # Overall rating
    if not _floats_equal(a.overall_rating, b.overall_rating):
        return False
    # Player ratings lists
    if len(a.starting_player_ratings) != len(b.starting_player_ratings):
        return False
    for pa, pb in zip(a.starting_player_ratings, b.starting_player_ratings):
        if not _player_rating_equal(pa, pb):
            return False
    if len(a.substitute_player_ratings) != len(b.substitute_player_ratings):
        return False
    for pa, pb in zip(a.substitute_player_ratings, b.substitute_player_ratings):
        if not _player_rating_equal(pa, pb):
            return False
    if a.motm_winners != b.motm_winners:
        return False
    if a.total_responses != b.total_responses:
        return False
    if a.formation != b.formation:
        return False
    return True


# ---------------------------------------------------------------------------
# Property 8: JSON Serialization Round-Trip
# ---------------------------------------------------------------------------

@given(results=compiled_results_st)
@settings(max_examples=100)
def test_json_round_trip(results: CompiledResults) -> None:
    """Serializing to dict and back SHALL produce an equivalent object.

    **Validates: Requirements 6.1, 6.2, 6.3**
    """
    restored = CompiledResults.from_dict(results.to_dict())
    assert _compiled_results_equal(results, restored)


# ---------------------------------------------------------------------------
# Unit tests for compile_responses (Task 5.1)
# ---------------------------------------------------------------------------

import numpy as np

from spurs_survey.models import MatchData, PlayerInfo, SubstitutionEvent
from spurs_survey.results import compile_responses, _compute_rating_stats, _determine_motm_winners


def _make_match_data(
    *,
    num_starters: int = 3,
    subs: list[tuple[str, str, int]] | None = None,
    coach: str = "Postecoglou",
) -> MatchData:
    """Helper to build a minimal MatchData for testing."""
    starters = [
        PlayerInfo(name=f"Player{i}", position="CM")
        for i in range(1, num_starters + 1)
    ]
    substitutions = [
        SubstitutionEvent(player_in=s[0], player_out=s[1], minute=s[2])
        for s in (subs or [])
    ]
    return MatchData(
        match_id=1,
        home_team="Tottenham Hotspur",
        away_team="Newcastle",
        competition="Premier League",
        matchday="Week 3",
        date="2024-09-01",
        venue="Tottenham Hotspur Stadium",
        formation="4-3-3",
        coach=coach,
        starting_players=starters,
        substitutions=substitutions,
        is_tottenham_home=True,
        home_score=2,
        away_score=1,
    )


def test_compile_responses_basic():
    """compile_responses computes correct mean/stddev and response count."""
    md = _make_match_data(num_starters=2)
    responses = [
        {
            "Tottenham Hotspur — Team Rating": "7",
            "Newcastle — Team Rating": "5",
            "Referee Rating": "6",
            "Postecoglou — Starting Eleven Selection": "8",
            "Postecoglou — On-Field Tactics": "7",
            "Postecoglou — Substitution Decisions": "6",
            "Player1 — Rating": "8",
            "Player2 — Rating": "6",
            "Man of the Match": "Player1",
        },
        {
            "Tottenham Hotspur — Team Rating": "5",
            "Newcastle — Team Rating": "7",
            "Referee Rating": "4",
            "Postecoglou — Starting Eleven Selection": "6",
            "Postecoglou — On-Field Tactics": "5",
            "Postecoglou — Substitution Decisions": "4",
            "Player1 — Rating": "6",
            "Player2 — Rating": "8",
            "Man of the Match": "Player1",
        },
    ]

    result = compile_responses(responses, md)

    assert result.total_responses == 2
    assert result.match_id == 1
    assert result.formation == "4-3-3"

    # Team rating: mean of [7, 5] = 6.0
    assert np.isclose(result.team_rating.mean, 6.0)
    # Player1: mean of [8, 6] = 7.0, Player2: mean of [6, 8] = 7.0
    assert np.isclose(result.starting_player_ratings[0].rating.mean, 7.0)
    assert np.isclose(result.starting_player_ratings[1].rating.mean, 7.0)
    # Overall = mean of player means = (7 + 7) / 2 = 7.0
    assert np.isclose(result.overall_rating, 7.0)
    # MOTM: Player1 has 2 votes
    assert result.motm_winners == ["Player1"]
    assert result.starting_player_ratings[0].is_motm is True
    assert result.starting_player_ratings[1].is_motm is False


def test_compile_responses_with_subs():
    """Substitute players are included in ratings and overall."""
    md = _make_match_data(
        num_starters=2,
        subs=[("SubPlayer", "Player2", 60)],
    )
    responses = [
        {
            "Tottenham Hotspur — Team Rating": "7",
            "Newcastle — Team Rating": "5",
            "Referee Rating": "6",
            "Postecoglou — Starting Eleven Selection": "7",
            "Postecoglou — On-Field Tactics": "7",
            "Postecoglou — Substitution Decisions": "7",
            "Player1 — Rating": "8",
            "Player2 — Rating": "6",
            "SubPlayer — Rating": "7",
            "Man of the Match": "SubPlayer",
        },
    ]

    result = compile_responses(responses, md)

    assert len(result.substitute_player_ratings) == 1
    assert result.substitute_player_ratings[0].name == "SubPlayer"
    assert np.isclose(result.substitute_player_ratings[0].rating.mean, 7.0)
    assert result.motm_winners == ["SubPlayer"]
    assert result.substitute_player_ratings[0].is_motm is True
    # Overall = mean of [8, 6, 7] = 7.0
    assert np.isclose(result.overall_rating, 7.0)


def test_compile_responses_motm_tie():
    """Tied MOTM votes produce multiple winners."""
    md = _make_match_data(num_starters=2)
    responses = [
        {
            "Player1 — Rating": "8",
            "Player2 — Rating": "7",
            "Man of the Match": "Player1",
        },
        {
            "Player1 — Rating": "7",
            "Player2 — Rating": "8",
            "Man of the Match": "Player2",
        },
    ]

    result = compile_responses(responses, md)

    assert sorted(result.motm_winners) == ["Player1", "Player2"]


def test_compile_responses_empty():
    """Zero responses produce zero-valued stats."""
    md = _make_match_data(num_starters=2)
    result = compile_responses([], md)

    assert result.total_responses == 0
    assert result.team_rating.mean == 0.0
    assert result.motm_winners == []


def test_compute_rating_stats_single_value():
    """Single rating has zero stddev."""
    stats = _compute_rating_stats([7])
    assert stats.mean == 7.0
    assert stats.std_dev == 0.0


def test_determine_motm_winners_empty():
    """No votes returns empty list."""
    assert _determine_motm_winners([], "Man of the Match") == []
    assert _determine_motm_winners([{}], "Man of the Match") == []


# ---------------------------------------------------------------------------
# Property 6: Statistics Computation Correctness
# ---------------------------------------------------------------------------

@given(ratings=st.lists(st.integers(min_value=0, max_value=10), min_size=1, max_size=100))
@settings(max_examples=100)
def test_statistics_computation_correctness(ratings: list[int]) -> None:
    """For any list of 0-10 integer ratings with at least one entry, the
    computed mean SHALL equal the arithmetic mean and the computed standard
    deviation SHALL equal the population standard deviation.

    **Validates: Requirements 3.1, 3.4, 3.5**
    """
    stats = _compute_rating_stats(ratings)

    expected_mean = sum(ratings) / len(ratings)
    variance = sum((r - expected_mean) ** 2 for r in ratings) / len(ratings)
    expected_std = variance ** 0.5

    assert math.isclose(stats.mean, expected_mean, rel_tol=1e-9, abs_tol=1e-12), (
        f"Mean mismatch: got {stats.mean}, expected {expected_mean}"
    )
    assert math.isclose(stats.std_dev, expected_std, rel_tol=1e-9, abs_tol=1e-12), (
        f"Stddev mismatch: got {stats.std_dev}, expected {expected_std}"
    )


# ---------------------------------------------------------------------------
# Property 7: Man of the Match Winner Determination
# ---------------------------------------------------------------------------

@given(
    votes=st.lists(
        st.text(
            alphabet=st.characters(whitelist_categories=("L", "N"), min_codepoint=65, max_codepoint=122),
            min_size=1,
            max_size=20,
        ),
        min_size=1,
        max_size=50,
    )
)
@settings(max_examples=100)
def test_motm_winner_determination(votes: list[str]) -> None:
    """For any list of MOTM votes, the reported winners SHALL be exactly the
    set of players whose vote count equals the maximum vote count.

    **Validates: Requirements 3.2, 3.3**
    """
    from collections import Counter

    # Build responses in the format _determine_motm_winners expects
    responses = [{"Man of the Match": v} for v in votes]
    winners = _determine_motm_winners(responses, "Man of the Match")

    counts = Counter(votes)
    max_count = max(counts.values())
    expected_winners = sorted(name for name, cnt in counts.items() if cnt == max_count)

    assert sorted(winners) == expected_winners, (
        f"Winners mismatch: got {sorted(winners)}, expected {expected_winners}"
    )
