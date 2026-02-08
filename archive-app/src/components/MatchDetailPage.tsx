import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { MatchDetail } from './MatchDetail';
import type { Match, PlayerRating } from '../types';

interface RawMatchDetail {
    match_id: number;
    metadata: {
        opponent: string;
        competition: string;
        matchday: string;
        date: string;
        venue: string;
        home_score: number;
        away_score: number;
        is_tottenham_home: boolean;
    };
    formation: string;
    team_rating: { mean: number; std_dev: number };
    opponent_rating: { mean: number; std_dev: number };
    referee_rating: { mean: number; std_dev: number };
    coach_ratings: {
        name: string;
        starting_eleven: { mean: number; std_dev: number };
        on_field_tactics: { mean: number; std_dev: number };
        substitutions: { mean: number; std_dev: number };
    };
    overall_rating: number;
    starting_players: Array<{
        name: string;
        position: string;
        image_path: string | null;
        rating: { mean: number; std_dev: number };
        is_starter: boolean;
        goals: number;
        assists: number;
        own_goals: number;
        is_motm: boolean;
    }>;
    substitute_players: Array<{
        name: string;
        position: string;
        image_path: string | null;
        rating: { mean: number; std_dev: number };
        is_starter: boolean;
        goals: number;
        assists: number;
        own_goals: number;
        is_motm: boolean;
    }>;
    motm_winners: string[];
    total_responses: number;
}

function parseDetail(raw: RawMatchDetail): Match {
    const m = raw.metadata;
    const isHome = m.is_tottenham_home;
    const spursScore = isHome ? m.home_score : m.away_score;
    const oppScore = isHome ? m.away_score : m.home_score;
    const score = isHome
        ? `${m.home_score} - ${m.away_score}`
        : `${m.away_score} - ${m.home_score}`;
    const result = spursScore > oppScore ? 'W' : spursScore < oppScore ? 'L' : 'D';

    const allPlayers = [...raw.starting_players, ...raw.substitute_players];
    const playerRatings: PlayerRating[] = allPlayers.map((p) => ({
        name: p.name,
        position: p.position,
        rating: p.rating.mean,
        stdDev: p.rating.std_dev,
        votes: 0,
        goals: p.goals,
        assists: p.assists,
        ownGoals: p.own_goals,
        isMotm: p.is_motm,
        isStarter: p.is_starter,
    }));

    return {
        matchId: raw.match_id,
        opponent: m.opponent,
        competition: m.competition,
        matchday: m.matchday,
        date: m.date,
        venue: m.venue,
        homeScore: m.home_score,
        awayScore: m.away_score,
        isTottenhamHome: m.is_tottenham_home,
        score,
        result,
        homeAway: isHome ? 'Home' : 'Away',
        averageRating: raw.overall_rating,
        totalVotes: raw.total_responses,
        motm: raw.motm_winners.join(', '),
        formation: raw.formation,
        playerRatings,
        teamRating: { mean: raw.team_rating.mean, stdDev: raw.team_rating.std_dev },
        opponentRating: { mean: raw.opponent_rating.mean, stdDev: raw.opponent_rating.std_dev },
        refereeRating: { mean: raw.referee_rating.mean, stdDev: raw.referee_rating.std_dev },
        coachRatings: {
            name: raw.coach_ratings.name,
            startingEleven: { mean: raw.coach_ratings.starting_eleven.mean, stdDev: raw.coach_ratings.starting_eleven.std_dev },
            onFieldTactics: { mean: raw.coach_ratings.on_field_tactics.mean, stdDev: raw.coach_ratings.on_field_tactics.std_dev },
            substitutions: { mean: raw.coach_ratings.substitutions.mean, stdDev: raw.coach_ratings.substitutions.std_dev },
        },
    };
}

export function MatchDetailPage() {
    const { matchId } = useParams<{ matchId: string }>();
    const [match, setMatch] = useState<Match | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!matchId) return;
        fetch(`${import.meta.env.BASE_URL}data/matches/${matchId}/results.json`)
            .then((res) => {
                if (!res.ok) throw new Error('Not found');
                return res.json();
            })
            .then((data: RawMatchDetail) => {
                setMatch(parseDetail(data));
                setLoading(false);
            })
            .catch(() => {
                setError('Match not found.');
                setLoading(false);
            });
    }, [matchId]);

    if (loading) {
        return <p className="text-[#8b949e] text-lg text-center py-12">Loading match details...</p>;
    }

    if (error || !match) {
        return <p className="text-[#8b949e] text-lg text-center py-12">{error || 'Match not found.'}</p>;
    }

    return <MatchDetail match={match} />;
}
