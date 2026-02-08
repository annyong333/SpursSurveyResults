"""Results compiler — computes statistics from survey responses.

Transforms raw Google Forms response dicts into a CompiledResults object
with mean/stddev ratings, MOTM winners, and overall rating.
"""

from __future__ import annotations

from collections import Counter

import numpy as np

from spurs_survey.models import (
    CoachRatings,
    CompiledResults,
    MatchData,
    MatchMetadata,
    PlayerRating,
    RatingStats,
)


def _compute_rating_stats(values: list[int | float]) -> RatingStats:
    """Compute mean and population standard deviation for a list of ratings."""
    arr = np.array(values, dtype=float)
    return RatingStats(
        mean=float(np.mean(arr)),
        std_dev=float(np.std(arr, ddof=0)),
    )


def _extract_ratings(responses: list[dict], key: str) -> list[int]:
    """Pull integer ratings for *key* from response dicts, skipping blanks."""
    values: list[int] = []
    for resp in responses:
        raw = resp.get(key)
        if raw is not None and raw != "":
            try:
                values.append(int(raw))
            except (ValueError, TypeError):
                continue
    return values


def _determine_motm_winners(responses: list[dict], motm_key: str) -> list[str]:
    """Return the player(s) with the most MOTM votes, handling ties."""
    votes: list[str] = []
    for resp in responses:
        vote = resp.get(motm_key)
        if vote and isinstance(vote, str) and vote.strip():
            votes.append(vote.strip())
    if not votes:
        return []
    counts = Counter(votes)
    max_count = max(counts.values())
    return sorted(name for name, cnt in counts.items() if cnt == max_count)


def compile_responses(
    responses: list[dict],
    match_data: MatchData,
) -> CompiledResults:
    """Compile raw survey responses into structured statistics.

    Parameters
    ----------
    responses:
        List of dicts keyed by question title (as produced by
        ``survey.fetch_responses``).
    match_data:
        The match data used to generate the survey.

    Returns
    -------
    CompiledResults
        Compiled statistics including per-entity ratings, MOTM winners,
        overall rating, and total response count.
    """
    opponent = (
        match_data.away_team
        if match_data.is_tottenham_home
        else match_data.home_team
    )
    coach_name = match_data.coach or "Manager"

    # --- Entity rating keys (must match survey.build_survey_structure titles) ---
    team_key = "Tottenham Hotspur — Team Rating"
    opponent_key = f"{opponent} — Team Rating"
    referee_key = "Referee Rating"
    coach_xi_key = f"{coach_name} — Starting Eleven Selection"
    coach_tactics_key = f"{coach_name} — On-Field Tactics"
    coach_subs_key = f"{coach_name} — Substitution Decisions"
    motm_key = "Man of the Match"

    # --- Compute entity ratings ---
    def _stats_for(key: str) -> RatingStats:
        vals = _extract_ratings(responses, key)
        if not vals:
            return RatingStats(mean=0.0, std_dev=0.0)
        return _compute_rating_stats(vals)

    team_rating = _stats_for(team_key)
    opponent_rating = _stats_for(opponent_key)
    referee_rating = _stats_for(referee_key)

    coach_ratings = CoachRatings(
        name=coach_name,
        starting_eleven=_stats_for(coach_xi_key),
        on_field_tactics=_stats_for(coach_tactics_key),
        substitutions=_stats_for(coach_subs_key),
    )

    # --- Player ratings ---
    sub_names = [sub.player_in for sub in match_data.substitutions]
    # Build a lookup for player info from starting lineup
    starter_info = {p.name: p for p in match_data.starting_players}

    starting_player_ratings: list[PlayerRating] = []
    for player in match_data.starting_players:
        key = f"{player.name} — Rating"
        stats = _stats_for(key)
        starting_player_ratings.append(PlayerRating(
            name=player.name,
            position=player.position,
            image_path=player.image_path,
            rating=stats,
            is_starter=True,
        ))

    substitute_player_ratings: list[PlayerRating] = []
    for name in sub_names:
        key = f"{name} — Rating"
        stats = _stats_for(key)
        substitute_player_ratings.append(PlayerRating(
            name=name,
            position="SUB",
            image_path=None,
            rating=stats,
            is_starter=False,
        ))

    # --- Overall rating = mean of all player rating means ---
    all_player_means = (
        [pr.rating.mean for pr in starting_player_ratings]
        + [pr.rating.mean for pr in substitute_player_ratings]
    )
    overall_rating = float(np.mean(all_player_means)) if all_player_means else 0.0

    # --- MOTM ---
    motm_winners = _determine_motm_winners(responses, motm_key)

    # Mark MOTM winners on player ratings
    motm_set = set(motm_winners)
    for pr in starting_player_ratings:
        pr.is_motm = pr.name in motm_set
    for pr in substitute_player_ratings:
        pr.is_motm = pr.name in motm_set

    # --- Metadata ---
    metadata = MatchMetadata(
        opponent=opponent,
        competition=match_data.competition,
        matchday=match_data.matchday,
        date=match_data.date,
        venue=match_data.venue,
        home_score=match_data.home_score or 0,
        away_score=match_data.away_score or 0,
        is_tottenham_home=match_data.is_tottenham_home,
    )

    return CompiledResults(
        match_id=match_data.match_id,
        match_metadata=metadata,
        team_rating=team_rating,
        opponent_rating=opponent_rating,
        referee_rating=referee_rating,
        coach_ratings=coach_ratings,
        overall_rating=overall_rating,
        starting_player_ratings=starting_player_ratings,
        substitute_player_ratings=substitute_player_ratings,
        motm_winners=motm_winners,
        total_responses=len(responses),
        formation=match_data.formation,
    )
