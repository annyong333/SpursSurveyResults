"""Property-based tests for infographic generation.

Feature: spurs-survey-automation, Property 9: Infographic Output Dimensions
Feature: spurs-survey-automation, Property 11: Missing Player Images Do Not Cause Failures
"""

from __future__ import annotations

import io
import os
import tempfile

from hypothesis import given, settings
from hypothesis import strategies as st
from PIL import Image

from spurs_survey.infographic import generate_infographic
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

rating_floats = st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)

rating_stats_st = st.builds(
    RatingStats,
    mean=rating_floats,
    std_dev=st.floats(min_value=0.0, max_value=5.0, allow_nan=False, allow_infinity=False),
)

# Player ratings that always have None image_path (for Property 11)
player_rating_none_image_st = st.builds(
    PlayerRating,
    name=st.text(alphabet=st.characters(whitelist_categories=("L", "N", "Zs")), min_size=1, max_size=15),
    position=st.sampled_from(["GK", "CB", "LB", "RB", "CM", "DM", "AM", "LW", "RW", "FW"]),
    image_path=st.none(),
    rating=rating_stats_st,
    is_starter=st.just(True),
    goals=st.integers(min_value=0, max_value=3),
    assists=st.integers(min_value=0, max_value=3),
    own_goals=st.integers(min_value=0, max_value=1),
    is_motm=st.booleans(),
)

# Player ratings with a mix of None and non-existent paths
player_rating_mixed_image_st = st.builds(
    PlayerRating,
    name=st.text(alphabet=st.characters(whitelist_categories=("L", "N", "Zs")), min_size=1, max_size=15),
    position=st.sampled_from(["GK", "CB", "LB", "RB", "CM", "DM", "AM", "LW", "RW", "FW"]),
    image_path=st.one_of(st.none(), st.just("/nonexistent/fake_player.png")),
    rating=rating_stats_st,
    is_starter=st.booleans(),
    goals=st.integers(min_value=0, max_value=3),
    assists=st.integers(min_value=0, max_value=3),
    own_goals=st.integers(min_value=0, max_value=1),
    is_motm=st.booleans(),
)

match_metadata_st = st.builds(
    MatchMetadata,
    opponent=st.text(alphabet=st.characters(whitelist_categories=("L",)), min_size=1, max_size=15),
    competition=st.just("Premier League"),
    matchday=st.just("Week 5"),
    date=st.just("2024-09-01"),
    venue=st.text(alphabet=st.characters(whitelist_categories=("L",)), min_size=1, max_size=20),
    home_score=st.integers(min_value=0, max_value=9),
    away_score=st.integers(min_value=0, max_value=9),
    is_tottenham_home=st.booleans(),
)

coach_ratings_st = st.builds(
    CoachRatings,
    name=st.text(alphabet=st.characters(whitelist_categories=("L",)), min_size=1, max_size=15),
    starting_eleven=rating_stats_st,
    on_field_tactics=rating_stats_st,
    substitutions=rating_stats_st,
)

formations_st = st.sampled_from(["4-3-3", "4-4-2", "3-5-2", "4-2-3-1", "3-4-3", "5-3-2", "4-1-4-1"])

compiled_results_st = st.builds(
    CompiledResults,
    match_id=st.integers(min_value=1, max_value=99999),
    match_metadata=match_metadata_st,
    team_rating=rating_stats_st,
    opponent_rating=rating_stats_st,
    referee_rating=rating_stats_st,
    coach_ratings=coach_ratings_st,
    overall_rating=rating_floats,
    starting_player_ratings=st.lists(player_rating_mixed_image_st, min_size=11, max_size=11),
    substitute_player_ratings=st.lists(player_rating_mixed_image_st, min_size=0, max_size=5),
    motm_winners=st.lists(st.text(alphabet=st.characters(whitelist_categories=("L",)), min_size=1, max_size=15), min_size=0, max_size=2),
    total_responses=st.integers(min_value=1, max_value=500),
    formation=formations_st,
)

# Strategy where ALL player images are None
compiled_results_no_images_st = st.builds(
    CompiledResults,
    match_id=st.integers(min_value=1, max_value=99999),
    match_metadata=match_metadata_st,
    team_rating=rating_stats_st,
    opponent_rating=rating_stats_st,
    referee_rating=rating_stats_st,
    coach_ratings=coach_ratings_st,
    overall_rating=rating_floats,
    starting_player_ratings=st.lists(player_rating_none_image_st, min_size=11, max_size=11),
    substitute_player_ratings=st.lists(player_rating_none_image_st, min_size=0, max_size=5),
    motm_winners=st.lists(st.text(alphabet=st.characters(whitelist_categories=("L",)), min_size=1, max_size=15), min_size=0, max_size=2),
    total_responses=st.integers(min_value=1, max_value=500),
    formation=formations_st,
)


# ---------------------------------------------------------------------------
# Property 9: Infographic Output Dimensions
# ---------------------------------------------------------------------------

@given(results=compiled_results_st)
@settings(max_examples=20, deadline=30000)
def test_infographic_output_dimensions(results: CompiledResults) -> None:
    """Property 9: For any valid CompiledResults, the generated infographic
    SHALL have a 16:9 aspect ratio (1920x1080).

    **Validates: Requirements 4.1**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "infographic.png")
        generate_infographic(results, quote="Test quote", photo_path="", output_path=out)

        assert os.path.isfile(out), "Infographic PNG was not created"

        img = Image.open(out)
        assert img.size == (1920, 1080), f"Expected 1920x1080, got {img.size}"
        # Verify 16:9 ratio
        assert img.size[0] / img.size[1] == 1920 / 1080


# ---------------------------------------------------------------------------
# Property 11: Missing Player Images Do Not Cause Failures
# ---------------------------------------------------------------------------

@given(results=compiled_results_no_images_st)
@settings(max_examples=20, deadline=30000)
def test_missing_player_images_no_failures(results: CompiledResults) -> None:
    """Property 11: For any valid CompiledResults where players have None
    image_path, the infographic generator SHALL produce a valid PNG without
    raising an exception.

    **Validates: Requirements 4.9**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "infographic.png")
        # This must not raise
        generate_infographic(results, quote="Quote", photo_path="", output_path=out)

        assert os.path.isfile(out), "Infographic PNG was not created"

        # Verify it's a valid PNG
        img = Image.open(out)
        img.verify()  # raises if not a valid image
