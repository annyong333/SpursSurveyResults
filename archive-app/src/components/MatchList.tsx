import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Download } from 'lucide-react';
import type { Match } from '../types';

interface MatchListProps {
    matches: Match[];
}

export function MatchList({ matches }: MatchListProps) {
    const [opponent, setOpponent] = useState('');
    const [competition, setCompetition] = useState('');
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');

    const opponents = [...new Set(matches.map((m) => m.opponent))].sort();
    const competitions = [...new Set(matches.map((m) => m.competition))].sort();

    const filtered = matches.filter((m) => {
        if (opponent && m.opponent !== opponent) return false;
        if (competition && m.competition !== competition) return false;
        if (dateFrom && m.date < dateFrom) return false;
        if (dateTo && m.date > dateTo) return false;
        return true;
    });

    const clearFilters = () => {
        setOpponent('');
        setCompetition('');
        setDateFrom('');
        setDateTo('');
    };

    const getResultColor = (result: string) => {
        switch (result) {
            case 'W': return 'bg-green-600';
            case 'L': return 'bg-red-600';
            case 'D': return 'bg-yellow-600';
            default: return 'bg-gray-600';
        }
    };

    return (
        <div>
            {/* Filters */}
            <div className="flex flex-wrap gap-4 items-end mb-6">
                <div className="flex flex-col gap-1">
                    <label className="text-xs text-[#8b949e] uppercase tracking-wider font-semibold">
                        Opponent
                    </label>
                    <select
                        value={opponent}
                        onChange={(e) => setOpponent(e.target.value)}
                        className="bg-[#161b22] border border-[#30363d] text-[#c9d1d9] rounded px-3 py-2 text-sm focus:border-[#d4a843] focus:outline-none"
                    >
                        <option value="">All opponents</option>
                        {opponents.map((o) => (
                            <option key={o} value={o}>{o}</option>
                        ))}
                    </select>
                </div>
                <div className="flex flex-col gap-1">
                    <label className="text-xs text-[#8b949e] uppercase tracking-wider font-semibold">
                        Competition
                    </label>
                    <select
                        value={competition}
                        onChange={(e) => setCompetition(e.target.value)}
                        className="bg-[#161b22] border border-[#30363d] text-[#c9d1d9] rounded px-3 py-2 text-sm focus:border-[#d4a843] focus:outline-none"
                    >
                        <option value="">All competitions</option>
                        {competitions.map((c) => (
                            <option key={c} value={c}>{c}</option>
                        ))}
                    </select>
                </div>
                <div className="flex flex-col gap-1">
                    <label className="text-xs text-[#8b949e] uppercase tracking-wider font-semibold">From</label>
                    <input
                        type="date"
                        value={dateFrom}
                        onChange={(e) => setDateFrom(e.target.value)}
                        className="bg-[#161b22] border border-[#30363d] text-[#c9d1d9] rounded px-3 py-2 text-sm focus:border-[#d4a843] focus:outline-none"
                    />
                </div>
                <div className="flex flex-col gap-1">
                    <label className="text-xs text-[#8b949e] uppercase tracking-wider font-semibold">To</label>
                    <input
                        type="date"
                        value={dateTo}
                        onChange={(e) => setDateTo(e.target.value)}
                        className="bg-[#161b22] border border-[#30363d] text-[#c9d1d9] rounded px-3 py-2 text-sm focus:border-[#d4a843] focus:outline-none"
                    />
                </div>
                <button
                    onClick={clearFilters}
                    className="border border-[#30363d] text-[#d4a843] rounded px-4 py-2 text-sm font-semibold hover:bg-[#161b22] transition-colors"
                >
                    Clear filters
                </button>
                <a
                    href={`${import.meta.env.BASE_URL}data/all_ratings.csv`}
                    download="all_ratings.csv"
                    className="flex items-center gap-1.5 border border-[#30363d] text-[#c9d1d9] rounded px-4 py-2 text-sm font-semibold hover:bg-[#161b22] hover:text-[#d4a843] transition-colors ml-auto"
                >
                    <Download size={14} />
                    Download CSV
                </a>
            </div>

            {/* Match Cards */}
            {filtered.length === 0 ? (
                <p className="text-[#8b949e] text-center py-12">No matches found.</p>
            ) : (
                <div className="flex flex-col gap-2">
                    {filtered.map((match) => {
                        const formatDate = new Date(match.date).toLocaleDateString('en-GB', {
                            day: 'numeric', month: 'short', year: 'numeric',
                        });
                        return (
                            <Link
                                key={match.matchId}
                                to={`/match/${match.matchId}`}
                                className="grid grid-cols-[100px_1fr_auto_auto] gap-4 items-center p-4 bg-[#161b22] rounded-lg border-l-[3px] border-[#132257] hover:border-[#d4a843] hover:bg-[#1c2333] transition-all text-left w-full"
                            >
                                <span className="text-sm text-[#8b949e]">{formatDate}</span>
                                <span className="text-white font-semibold">{match.opponent}</span>
                                <div className="flex items-center gap-2">
                                    <span className={`${getResultColor(match.result)} text-white text-xs font-bold px-2 py-1 rounded`}>
                                        {match.result}
                                    </span>
                                    <span className="text-white font-bold text-lg">{match.score}</span>
                                </div>
                                <span className="text-sm text-[#8b949e] text-right">
                                    {match.competition} · {match.homeAway}
                                </span>
                            </Link>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
