import { useState, useEffect } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { MatchList } from './components/MatchList';
import { MatchDetailPage } from './components/MatchDetailPage';
import type { Match } from './types';

interface RawMatchIndex {
  match_id: number;
  opponent: string;
  competition: string;
  matchday: string;
  date: string;
  venue: string;
  home_score: number;
  away_score: number;
  is_tottenham_home: boolean;
}

function parseMatch(raw: RawMatchIndex): Match {
  const isHome = raw.is_tottenham_home;
  const spursScore = isHome ? raw.home_score : raw.away_score;
  const oppScore = isHome ? raw.away_score : raw.home_score;
  const score = isHome
    ? `${raw.home_score} - ${raw.away_score}`
    : `${raw.away_score} - ${raw.home_score}`;
  const result = spursScore > oppScore ? 'W' : spursScore < oppScore ? 'L' : 'D';

  return {
    matchId: raw.match_id,
    opponent: raw.opponent,
    competition: raw.competition,
    matchday: raw.matchday,
    date: raw.date,
    venue: raw.venue,
    homeScore: raw.home_score,
    awayScore: raw.away_score,
    isTottenhamHome: raw.is_tottenham_home,
    score,
    result,
    homeAway: isHome ? 'Home' : 'Away',
    averageRating: 0,
    totalVotes: 0,
    motm: '',
    formation: '',
    playerRatings: [],
    teamRating: { mean: 0, stdDev: 0 },
    opponentRating: { mean: 0, stdDev: 0 },
    refereeRating: { mean: 0, stdDev: 0 },
    coachRatings: {
      name: '',
      startingEleven: { mean: 0, stdDev: 0 },
      onFieldTactics: { mean: 0, stdDev: 0 },
      substitutions: { mean: 0, stdDev: 0 },
    },
  };
}

export default function App() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/matches.json`)
      .then((res) => res.json())
      .then((data: RawMatchIndex[]) => {
        const parsed = data.map(parseMatch);
        parsed.sort((a, b) => (b.date > a.date ? 1 : b.date < a.date ? -1 : 0));
        setMatches(parsed);
        setLoading(false);
      })
      .catch(() => {
        setError('Could not load match data.');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0d1117] flex items-center justify-center">
        <p className="text-[#8b949e] text-lg">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#0d1117] flex items-center justify-center">
        <p className="text-[#8b949e] text-lg">{error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0d1117]">
      <header className="bg-gradient-to-r from-[#132257] to-[#1a2d6b] border-b-2 border-[#d4a843]">
        <div className="max-w-5xl mx-auto px-6 py-5 flex items-center gap-4">
          <img
            src="https://upload.wikimedia.org/wikipedia/en/thumb/b/b4/Tottenham_Hotspur.svg/48px-Tottenham_Hotspur.svg.png"
            alt="Tottenham Hotspur"
            className="w-12 h-12 object-contain"
          />
          <div>
            <Link to="/" className="text-xl font-bold text-white hover:text-[#d4a843] transition-colors">
              r/coys Match Survey Results
            </Link>
            <p className="text-[#8b949e] text-sm">Post-match player rating archive</p>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        <Routes>
          <Route path="/" element={<MatchList matches={matches} />} />
          <Route path="/match/:matchId" element={<MatchDetailPage />} />
        </Routes>
      </main>
    </div>
  );
}
