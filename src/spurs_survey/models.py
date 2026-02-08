"""Data models for the Spurs Survey system."""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Match data models
# ---------------------------------------------------------------------------

@dataclass
class PlayerInfo:
    """A player in a match lineup."""

    name: str
    position: str
    image_path: str | None = None
    shirt_number: int | None = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "position": self.position,
            "image_path": self.image_path,
            "shirt_number": self.shirt_number,
        }

    @classmethod
    def from_dict(cls, d: dict) -> PlayerInfo:
        return cls(
            name=d["name"],
            position=d["position"],
            image_path=d.get("image_path"),
            shirt_number=d.get("shirt_number"),
        )


@dataclass
class SubstitutionEvent:
    """A substitution that occurred during a match."""

    player_in: str
    player_out: str
    minute: int

    def to_dict(self) -> dict:
        return {
            "player_in": self.player_in,
            "player_out": self.player_out,
            "minute": self.minute,
        }

    @classmethod
    def from_dict(cls, d: dict) -> SubstitutionEvent:
        return cls(
            player_in=d["player_in"],
            player_out=d["player_out"],
            minute=d["minute"],
        )


@dataclass
class MatchData:
    """All data for a single Tottenham match."""

    match_id: int
    home_team: str
    away_team: str
    competition: str
    matchday: str
    date: str
    venue: str
    formation: str
    coach: str
    starting_players: list[PlayerInfo] = field(default_factory=list)
    substitutions: list[SubstitutionEvent] = field(default_factory=list)
    is_tottenham_home: bool = True
    home_score: int | None = None
    away_score: int | None = None

    def to_dict(self) -> dict:
        return {
            "match_id": self.match_id,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "competition": self.competition,
            "matchday": self.matchday,
            "date": self.date,
            "venue": self.venue,
            "formation": self.formation,
            "coach": self.coach,
            "starting_players": [p.to_dict() for p in self.starting_players],
            "substitutions": [s.to_dict() for s in self.substitutions],
            "is_tottenham_home": self.is_tottenham_home,
            "home_score": self.home_score,
            "away_score": self.away_score,
        }

    @classmethod
    def from_dict(cls, d: dict) -> MatchData:
        return cls(
            match_id=d["match_id"],
            home_team=d["home_team"],
            away_team=d["away_team"],
            competition=d["competition"],
            matchday=d["matchday"],
            date=d["date"],
            venue=d["venue"],
            formation=d["formation"],
            coach=d["coach"],
            starting_players=[PlayerInfo.from_dict(p) for p in d.get("starting_players", [])],
            substitutions=[SubstitutionEvent.from_dict(s) for s in d.get("substitutions", [])],
            is_tottenham_home=d.get("is_tottenham_home", True),
            home_score=d.get("home_score"),
            away_score=d.get("away_score"),
        )


# ---------------------------------------------------------------------------
# Compiled results models
# ---------------------------------------------------------------------------

@dataclass
class RatingStats:
    """Mean and standard deviation for a rating."""

    mean: float
    std_dev: float

    def to_dict(self) -> dict:
        return {"mean": self.mean, "std_dev": self.std_dev}

    @classmethod
    def from_dict(cls, d: dict) -> RatingStats:
        return cls(mean=d["mean"], std_dev=d["std_dev"])


@dataclass
class PlayerRating:
    """Compiled rating data for a single player."""

    name: str
    position: str
    image_path: str | None
    rating: RatingStats
    is_starter: bool
    goals: int = 0
    assists: int = 0
    own_goals: int = 0
    is_motm: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "position": self.position,
            "image_path": self.image_path,
            "rating": self.rating.to_dict(),
            "is_starter": self.is_starter,
            "goals": self.goals,
            "assists": self.assists,
            "own_goals": self.own_goals,
            "is_motm": self.is_motm,
        }

    @classmethod
    def from_dict(cls, d: dict) -> PlayerRating:
        return cls(
            name=d["name"],
            position=d["position"],
            image_path=d.get("image_path"),
            rating=RatingStats.from_dict(d["rating"]),
            is_starter=d["is_starter"],
            goals=d.get("goals", 0),
            assists=d.get("assists", 0),
            own_goals=d.get("own_goals", 0),
            is_motm=d.get("is_motm", False),
        )


@dataclass
class MatchMetadata:
    """Identifying information for a match."""

    opponent: str
    competition: str
    matchday: str
    date: str
    venue: str
    home_score: int
    away_score: int
    is_tottenham_home: bool

    def to_dict(self) -> dict:
        return {
            "opponent": self.opponent,
            "competition": self.competition,
            "matchday": self.matchday,
            "date": self.date,
            "venue": self.venue,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "is_tottenham_home": self.is_tottenham_home,
        }

    @classmethod
    def from_dict(cls, d: dict) -> MatchMetadata:
        return cls(
            opponent=d["opponent"],
            competition=d["competition"],
            matchday=d["matchday"],
            date=d["date"],
            venue=d["venue"],
            home_score=d["home_score"],
            away_score=d["away_score"],
            is_tottenham_home=d["is_tottenham_home"],
        )


@dataclass
class CoachRatings:
    """Tactical ratings for the coach."""

    name: str
    starting_eleven: RatingStats
    on_field_tactics: RatingStats
    substitutions: RatingStats

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "starting_eleven": self.starting_eleven.to_dict(),
            "on_field_tactics": self.on_field_tactics.to_dict(),
            "substitutions": self.substitutions.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> CoachRatings:
        return cls(
            name=d["name"],
            starting_eleven=RatingStats.from_dict(d["starting_eleven"]),
            on_field_tactics=RatingStats.from_dict(d["on_field_tactics"]),
            substitutions=RatingStats.from_dict(d["substitutions"]),
        )


@dataclass
class CompiledResults:
    """Full compiled survey results for a match."""

    match_id: int
    match_metadata: MatchMetadata
    team_rating: RatingStats
    opponent_rating: RatingStats
    referee_rating: RatingStats
    coach_ratings: CoachRatings
    overall_rating: float
    starting_player_ratings: list[PlayerRating] = field(default_factory=list)
    substitute_player_ratings: list[PlayerRating] = field(default_factory=list)
    motm_winners: list[str] = field(default_factory=list)
    total_responses: int = 0
    formation: str = "4-3-3"

    def to_dict(self) -> dict:
        return {
            "match_id": self.match_id,
            "metadata": self.match_metadata.to_dict(),
            "team_rating": self.team_rating.to_dict(),
            "opponent_rating": self.opponent_rating.to_dict(),
            "referee_rating": self.referee_rating.to_dict(),
            "coach_ratings": self.coach_ratings.to_dict(),
            "overall_rating": self.overall_rating,
            "starting_players": [p.to_dict() for p in self.starting_player_ratings],
            "substitute_players": [p.to_dict() for p in self.substitute_player_ratings],
            "motm_winners": self.motm_winners,
            "total_responses": self.total_responses,
            "formation": self.formation,
        }

    @classmethod
    def from_dict(cls, d: dict) -> CompiledResults:
        return cls(
            match_id=d["match_id"],
            match_metadata=MatchMetadata.from_dict(d["metadata"]),
            team_rating=RatingStats.from_dict(d["team_rating"]),
            opponent_rating=RatingStats.from_dict(d["opponent_rating"]),
            referee_rating=RatingStats.from_dict(d["referee_rating"]),
            coach_ratings=CoachRatings.from_dict(d["coach_ratings"]),
            overall_rating=d["overall_rating"],
            starting_player_ratings=[PlayerRating.from_dict(p) for p in d.get("starting_players", [])],
            substitute_player_ratings=[PlayerRating.from_dict(p) for p in d.get("substitute_players", [])],
            motm_winners=d.get("motm_winners", []),
            total_responses=d.get("total_responses", 0),
            formation=d.get("formation", "4-3-3"),
        )
