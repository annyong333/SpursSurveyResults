"""Formation layout mappings for infographic rendering.

Each formation maps to a list of (position_label, player_count) tuples,
ordered from front (attackers) to back (goalkeeper).
"""

FORMATION_LAYOUTS: dict[str, list[tuple[str, int]]] = {
    "4-3-3": [("FW", 3), ("MF", 3), ("DF", 4), ("GK", 1)],
    "4-4-2": [("FW", 2), ("MF", 4), ("DF", 4), ("GK", 1)],
    "3-5-2": [("FW", 2), ("MF", 5), ("DF", 3), ("GK", 1)],
    "4-2-3-1": [("FW", 1), ("AM", 3), ("DM", 2), ("DF", 4), ("GK", 1)],
    "3-4-3": [("FW", 3), ("MF", 4), ("DF", 3), ("GK", 1)],
    "5-3-2": [("FW", 2), ("MF", 3), ("DF", 5), ("GK", 1)],
    "4-1-4-1": [("FW", 1), ("MF", 4), ("DM", 1), ("DF", 4), ("GK", 1)],
}
