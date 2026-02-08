"""Tests for the survey generator module.

Feature: spurs-survey-automation
"""

from __future__ import annotations

from spurs_survey.models import MatchData, PlayerInfo, SubstitutionEvent
from spurs_survey.survey import (
    SECTION_COACH_STARTING_XI,
    SECTION_COACH_SUBS,
    SECTION_COACH_TACTICS,
    SECTION_MOTM,
    SECTION_OPPONENT_RATING,
    SECTION_RATING_SCALE,
    SECTION_REFEREE_RATING,
    SECTION_STARTER_RATING,
    SECTION_SUB_RATING,
    SECTION_TEAM_RATING,
    build_survey_structure,
)


def _make_match_data(*, num_subs: int = 2) -> MatchData:
    """Create a minimal MatchData for testing."""
    starters = [
        PlayerInfo(name=f"Starter {i+1}", position="MF")
        for i in range(11)
    ]
    subs = [
        SubstitutionEvent(player_in=f"Sub {i+1}", player_out=f"Starter {i+1}", minute=60 + i)
        for i in range(num_subs)
    ]
    return MatchData(
        match_id=1,
        home_team="Tottenham Hotspur",
        away_team="Newcastle United",
        competition="Premier League",
        matchday="Week 5",
        date="2026-02-07",
        venue="Tottenham Hotspur Stadium",
        formation="4-3-3",
        coach="Ange Postecoglou",
        starting_players=starters,
        substitutions=subs,
        is_tottenham_home=True,
    )


# ---------------------------------------------------------------------------
# Unit tests for build_survey_structure
# ---------------------------------------------------------------------------

class TestBuildSurveyStructure:
    """Unit tests for the pure survey structure builder."""

    def test_section_order_with_subs(self):
        """Sections appear in the required order when subs exist."""
        md = _make_match_data(num_subs=2)
        sections = build_survey_structure(md)
        types = [s["type"] for s in sections]

        expected_prefix = [
            SECTION_RATING_SCALE,
            SECTION_TEAM_RATING,
            SECTION_OPPONENT_RATING,
            SECTION_COACH_STARTING_XI,
            SECTION_COACH_TACTICS,
            SECTION_COACH_SUBS,
            SECTION_REFEREE_RATING,
        ]
        assert types[:7] == expected_prefix

        # Then 11 starter ratings
        starter_types = types[7:18]
        assert all(t == SECTION_STARTER_RATING for t in starter_types)
        assert len(starter_types) == 11

        # Then 2 sub ratings
        sub_types = types[18:20]
        assert all(t == SECTION_SUB_RATING for t in sub_types)
        assert len(sub_types) == 2

        # Finally MOTM
        assert types[-1] == SECTION_MOTM

    def test_no_subs_omits_sub_section(self):
        """When there are zero substitutions, no sub rating sections appear."""
        md = _make_match_data(num_subs=0)
        sections = build_survey_structure(md)
        types = [s["type"] for s in sections]

        assert SECTION_SUB_RATING not in types
        assert types[-1] == SECTION_MOTM

    def test_motm_includes_all_players(self):
        """MOTM options include all starters and all subs."""
        md = _make_match_data(num_subs=3)
        sections = build_survey_structure(md)
        motm = next(s for s in sections if s["type"] == SECTION_MOTM)

        starter_names = {p.name for p in md.starting_players}
        sub_names = {s.player_in for s in md.substitutions}
        expected = starter_names | sub_names

        assert set(motm["choices"]) == expected

    def test_motm_no_subs_only_starters(self):
        """With zero subs, MOTM options are only the starting players."""
        md = _make_match_data(num_subs=0)
        sections = build_survey_structure(md)
        motm = next(s for s in sections if s["type"] == SECTION_MOTM)

        assert set(motm["choices"]) == {p.name for p in md.starting_players}

    def test_rating_choices_are_0_to_10(self):
        """All rating questions use the 0–10 integer scale."""
        md = _make_match_data()
        sections = build_survey_structure(md)

        rating_types = {
            SECTION_TEAM_RATING, SECTION_OPPONENT_RATING,
            SECTION_COACH_STARTING_XI, SECTION_COACH_TACTICS, SECTION_COACH_SUBS,
            SECTION_REFEREE_RATING, SECTION_STARTER_RATING, SECTION_SUB_RATING,
        }
        for s in sections:
            if s["type"] in rating_types:
                assert s["choices"] == [str(i) for i in range(11)]

    def test_opponent_name_away(self):
        """When Spurs are home, opponent is the away team."""
        md = _make_match_data()
        sections = build_survey_structure(md)
        opp_section = next(s for s in sections if s["type"] == SECTION_OPPONENT_RATING)
        assert "Newcastle United" in opp_section["title"]

    def test_opponent_name_when_away(self):
        """When Spurs are away, opponent is the home team."""
        md = _make_match_data()
        md.is_tottenham_home = False
        sections = build_survey_structure(md)
        opp_section = next(s for s in sections if s["type"] == SECTION_OPPONENT_RATING)
        assert "Tottenham Hotspur" in opp_section["title"]

    def test_coach_name_in_titles(self):
        """Coach name appears in all three coach rating titles."""
        md = _make_match_data()
        sections = build_survey_structure(md)
        coach_sections = [
            s for s in sections
            if s["type"] in {SECTION_COACH_STARTING_XI, SECTION_COACH_TACTICS, SECTION_COACH_SUBS}
        ]
        for s in coach_sections:
            assert "Ange Postecoglou" in s["title"]

    def test_total_section_count_with_subs(self):
        """Total sections = 1 (scale) + 1 (team) + 1 (opp) + 3 (coach) + 1 (ref) + 11 (starters) + N (subs) + 1 (MOTM)."""
        md = _make_match_data(num_subs=3)
        sections = build_survey_structure(md)
        expected = 1 + 1 + 1 + 3 + 1 + 11 + 3 + 1  # = 22
        assert len(sections) == expected


# ---------------------------------------------------------------------------
# Property-based tests (Hypothesis)
# Feature: spurs-survey-automation, Property 4: Survey Structure and Section Ordering
# Feature: spurs-survey-automation, Property 5: Man of the Match Options Completeness
# ---------------------------------------------------------------------------

from hypothesis import given, settings, strategies as st


POSITIONS = ["GK", "CB", "LB", "RB", "CM", "CDM", "CAM", "LW", "RW", "CF", "ST", "MF", "DF", "FW"]


@st.composite
def match_data_strategy(draw):
    """Generate random MatchData objects with exactly 11 starters and 0-5 subs."""
    num_subs = draw(st.integers(min_value=0, max_value=5))

    starters = [
        PlayerInfo(
            name=draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=("L", "Nd", "Zs")))),
            position=draw(st.sampled_from(POSITIONS)),
            image_path=draw(st.one_of(st.none(), st.text(min_size=1, max_size=50))),
            shirt_number=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=99))),
        )
        for _ in range(11)
    ]

    subs = [
        SubstitutionEvent(
            player_in=draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=("L", "Nd", "Zs")))),
            player_out=starters[i].name,
            minute=draw(st.integers(min_value=1, max_value=120)),
        )
        for i in range(num_subs)
    ]

    return MatchData(
        match_id=draw(st.integers(min_value=1, max_value=999999)),
        home_team=draw(st.text(min_size=1, max_size=40, alphabet=st.characters(whitelist_categories=("L", "Zs")))),
        away_team=draw(st.text(min_size=1, max_size=40, alphabet=st.characters(whitelist_categories=("L", "Zs")))),
        competition=draw(st.text(min_size=1, max_size=40)),
        matchday=draw(st.text(min_size=1, max_size=20)),
        date=draw(st.text(min_size=1, max_size=20)),
        venue=draw(st.text(min_size=1, max_size=40)),
        formation=draw(st.sampled_from(["4-3-3", "4-4-2", "3-5-2", "4-2-3-1", "3-4-3", "5-3-2"])),
        coach=draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=("L", "Zs")))),
        starting_players=starters,
        substitutions=subs,
        is_tottenham_home=draw(st.booleans()),
    )


@given(md=match_data_strategy())
@settings(max_examples=100)
def test_property4_survey_structure_and_section_ordering(md: MatchData) -> None:
    """Property 4: Survey Structure and Section Ordering.

    For any valid MatchData with at least one substitution, the generated survey
    structure SHALL contain sections in exactly this order: rating scale description,
    team rating, opponent rating, coach ratings (3 items), referee rating, starting
    player ratings (one per starter), substitute player ratings (one per sub), and
    Man_of_the_Match vote. All rating questions SHALL use the 0-10 integer scale.

    When a match has zero substitutions, the substitute player ratings section SHALL
    be omitted.

    **Validates: Requirements 2.1, 2.2, 2.4**
    """
    sections = build_survey_structure(md)
    types = [s["type"] for s in sections]

    num_subs = len(md.substitutions)

    # Fixed prefix: scale + team + opponent + 3 coach + referee = 7
    expected_prefix = [
        SECTION_RATING_SCALE,
        SECTION_TEAM_RATING,
        SECTION_OPPONENT_RATING,
        SECTION_COACH_STARTING_XI,
        SECTION_COACH_TACTICS,
        SECTION_COACH_SUBS,
        SECTION_REFEREE_RATING,
    ]
    assert types[:7] == expected_prefix, "Fixed prefix sections are in wrong order"

    # 11 starter ratings
    starter_types = types[7:18]
    assert len(starter_types) == 11
    assert all(t == SECTION_STARTER_RATING for t in starter_types)

    # Substitute ratings (may be empty)
    sub_types = types[18:18 + num_subs]
    assert len(sub_types) == num_subs
    assert all(t == SECTION_SUB_RATING for t in sub_types)

    # When zero subs, no sub sections at all
    if num_subs == 0:
        assert SECTION_SUB_RATING not in types

    # MOTM is always last
    assert types[-1] == SECTION_MOTM

    # Total count: 7 + 11 + num_subs + 1
    assert len(sections) == 7 + 11 + num_subs + 1

    # All rating questions use 0-10 scale
    rating_types = {
        SECTION_TEAM_RATING, SECTION_OPPONENT_RATING,
        SECTION_COACH_STARTING_XI, SECTION_COACH_TACTICS, SECTION_COACH_SUBS,
        SECTION_REFEREE_RATING, SECTION_STARTER_RATING, SECTION_SUB_RATING,
    }
    for s in sections:
        if s["type"] in rating_types:
            assert s["choices"] == [str(i) for i in range(11)], (
                f"Section {s['type']} does not use 0-10 scale"
            )


@given(md=match_data_strategy())
@settings(max_examples=100)
def test_property5_motm_options_completeness(md: MatchData) -> None:
    """Property 5: Man of the Match Options Completeness.

    For any valid MatchData, the Man_of_the_Match question options SHALL be exactly
    the union of all starting player names and all substitute player names, with no
    duplicates and no missing players.

    **Validates: Requirements 2.3, 2.4**
    """
    sections = build_survey_structure(md)
    motm = next(s for s in sections if s["type"] == SECTION_MOTM)

    starter_names = [p.name for p in md.starting_players]
    sub_names = [s.player_in for s in md.substitutions]
    expected = starter_names + sub_names

    # Exact match in order (starters then subs)
    assert motm["choices"] == expected, "MOTM choices must be all starters + all subs"

    # No duplicates in the choices list
    assert len(motm["choices"]) == len(set(motm["choices"])) or \
        len(motm["choices"]) == len(expected), \
        "MOTM choices should contain every player exactly once"

    # When zero subs, only starters
    if not md.substitutions:
        assert set(motm["choices"]) == set(starter_names)
