"""Property tests for the results archive (Properties 12, 13)."""

from __future__ import annotations

from hypothesis import given, settings, strategies as st

from spurs_survey.archive import filter_matches, sort_matches

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

_opponents = st.sampled_from(["Arsenal", "Chelsea", "Newcastle", "Liverpool", "Man City"])
_competitions = st.sampled_from(["Premier League", "EFL Cup", "FA Cup", "Europa League"])

_match_entry = st.fixed_dictionaries({
    "match_id": st.integers(min_value=1, max_value=100_000),
    "opponent": _opponents,
    "competition": _competitions,
    "matchday": st.text(min_size=1, max_size=10),
    "date": st.dates().map(lambda d: d.isoformat()),
    "venue": st.text(min_size=1, max_size=30),
    "home_score": st.integers(min_value=0, max_value=9),
    "away_score": st.integers(min_value=0, max_value=9),
    "is_tottenham_home": st.booleans(),
})

_match_list = st.lists(_match_entry, min_size=0, max_size=30)


# ---------------------------------------------------------------------------
# Property 12: Archive Match Sorting
# ---------------------------------------------------------------------------

@given(entries=_match_list)
@settings(max_examples=200)
def test_property12_archive_match_sorting(entries: list[dict]) -> None:
    """For any list of match entries, sort_matches returns them in
    descending date order (most recent first).

    **Validates: Requirements 5.1**
    """
    # Feature: spurs-survey-automation, Property 12: Archive Match Sorting
    sorted_entries = sort_matches(entries)

    # Length preserved
    assert len(sorted_entries) == len(entries)

    # Descending date order
    for i in range(len(sorted_entries) - 1):
        assert sorted_entries[i]["date"] >= sorted_entries[i + 1]["date"]


# ---------------------------------------------------------------------------
# Property 13: Archive Filtering Correctness
# ---------------------------------------------------------------------------

@given(
    entries=_match_list,
    opponent=st.one_of(st.none(), _opponents),
    competition=st.one_of(st.none(), _competitions),
    date_from=st.one_of(st.none(), st.dates().map(lambda d: d.isoformat())),
    date_to=st.one_of(st.none(), st.dates().map(lambda d: d.isoformat())),
)
@settings(max_examples=200)
def test_property13_archive_filtering_correctness(
    entries: list[dict],
    opponent: str | None,
    competition: str | None,
    date_from: str | None,
    date_to: str | None,
) -> None:
    """For any list of match entries and any filter criteria, every match in
    the filtered results satisfies all conditions, and no qualifying match
    is excluded.

    **Validates: Requirements 5.3**
    """
    # Feature: spurs-survey-automation, Property 13: Archive Filtering Correctness
    filtered = filter_matches(
        entries,
        opponent=opponent,
        competition=competition,
        date_from=date_from,
        date_to=date_to,
    )

    # Every returned match satisfies all filters
    for m in filtered:
        if opponent:
            assert m["opponent"] == opponent
        if competition:
            assert m["competition"] == competition
        if date_from:
            assert m["date"] >= date_from
        if date_to:
            assert m["date"] <= date_to

    # No qualifying match is excluded
    filtered_ids = {id(m) for m in filtered}
    for m in entries:
        satisfies = True
        if opponent and m["opponent"] != opponent:
            satisfies = False
        if competition and m["competition"] != competition:
            satisfies = False
        if date_from and m["date"] < date_from:
            satisfies = False
        if date_to and m["date"] > date_to:
            satisfies = False
        if satisfies:
            assert id(m) in filtered_ids, f"Match {m} should be in filtered results"
