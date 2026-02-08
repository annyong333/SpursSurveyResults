"""Property-based tests for formation layouts.

Feature: spurs-survey-automation, Property 10: Formation Layout Produces Correct Player Count
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from spurs_survey.formations import FORMATION_LAYOUTS


# ---------------------------------------------------------------------------
# Property 10: Formation Layout Produces Correct Player Count
# ---------------------------------------------------------------------------

@given(formation=st.sampled_from(list(FORMATION_LAYOUTS.keys())))
@settings(max_examples=100)
def test_formation_layout_sums_to_eleven(formation: str) -> None:
    """For any supported formation, row player counts SHALL sum to exactly 11.

    **Validates: Requirements 4.3**
    """
    rows = FORMATION_LAYOUTS[formation]
    total = sum(count for _, count in rows)
    assert total == 11, f"Formation {formation} has {total} players, expected 11"
