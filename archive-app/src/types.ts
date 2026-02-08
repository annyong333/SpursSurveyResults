export interface PlayerRating {
    name: string;
    position: string;
    rating: number;
    stdDev: number;
    votes: number;
    goals: number;
    assists: number;
    ownGoals: number;
    isMotm: boolean;
    isStarter: boolean;
}

export interface Match {
    matchId: number;
    opponent: string;
    competition: string;
    matchday: string;
    date: string;
    venue: string;
    homeScore: number;
    awayScore: number;
    isTottenhamHome: boolean;
    score: string;
    result: 'W' | 'L' | 'D';
    homeAway: string;
    averageRating: number;
    totalVotes: number;
    motm: string;
    formation: string;
    playerRatings: PlayerRating[];
    teamRating: { mean: number; stdDev: number };
    opponentRating: { mean: number; stdDev: number };
    refereeRating: { mean: number; stdDev: number };
    coachRatings: {
        name: string;
        startingEleven: { mean: number; stdDev: number };
        onFieldTactics: { mean: number; stdDev: number };
        substitutions: { mean: number; stdDev: number };
    };
}
