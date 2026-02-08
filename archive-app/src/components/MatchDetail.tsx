import { Link } from 'react-router-dom';
import type { Match } from '../types';
import { ArrowLeft, Trophy, Users } from 'lucide-react';

interface MatchDetailProps {
    match: Match;
}

export function MatchDetail({ match }: MatchDetailProps) {
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-GB', {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
            year: 'numeric',
        });
    };

    const getResultColor = (result: string) => {
        switch (result) {
            case 'W': return 'bg-green-600';
            case 'L': return 'bg-red-600';
            case 'D': return 'bg-yellow-600';
            default: return 'bg-gray-600';
        }
    };

    const getResultText = (result: string) => {
        switch (result) {
            case 'W': return 'Victory';
            case 'L': return 'Defeat';
            case 'D': return 'Draw';
            default: return result;
        }
    };

    const getRatingColor = (rating: number) => {
        if (rating >= 9) return 'bg-gradient-to-r from-green-600 to-green-500';
        if (rating >= 8) return 'bg-gradient-to-r from-green-500 to-blue-500';
        if (rating >= 7) return 'bg-gradient-to-r from-blue-500 to-blue-600';
        if (rating >= 6) return 'bg-gradient-to-r from-yellow-500 to-yellow-600';
        if (rating >= 5) return 'bg-gradient-to-r from-orange-500 to-orange-600';
        return 'bg-gradient-to-r from-red-500 to-red-600';
    };

    const getPositionColor = (position: string) => {
        if (position === 'GK') return 'bg-yellow-500/20 text-yellow-400';
        if (['RB', 'CB', 'LB', 'DF'].includes(position)) return 'bg-blue-500/20 text-blue-400';
        if (['CM', 'AM', 'DM', 'MF'].includes(position)) return 'bg-green-500/20 text-green-400';
        return 'bg-purple-500/20 text-purple-400';
    };

    const sortedPlayers = [...match.playerRatings].sort((a, b) => b.rating - a.rating);
    const topRated = sortedPlayers[0];

    return (
        <div>
            {/* Back Button */}
            <Link
                to="/"
                className="flex items-center gap-2 text-[#58a6ff] hover:text-white mb-6 transition-colors"
            >
                <ArrowLeft className="w-5 h-5" />
                <span>Back to matches</span>
            </Link>

            {/* Match Header Card */}
            <div className="bg-gradient-to-r from-[#132257] to-[#1a2d6b] rounded-lg p-8 mb-8 border border-[#30363d]">
                <div className="flex items-center justify-between flex-wrap gap-4 mb-6">
                    <div>
                        <div className="flex items-center gap-3 mb-3">
                            <span
                                className={`${getResultColor(match.result)} text-white px-4 py-2 rounded-lg text-lg font-semibold`}
                            >
                                {getResultText(match.result)}
                            </span>
                            <span className="text-[#8b949e] text-lg">{match.homeAway}</span>
                        </div>
                        <h2 className="text-4xl text-white mb-2">
                            Tottenham Hotspur {match.score} {match.opponent}
                        </h2>
                        <p className="text-[#8b949e] text-lg">{formatDate(match.date)}</p>
                    </div>
                </div>

                <div className="flex items-center gap-2 mb-6">
                    <span className="inline-block bg-white/10 text-white px-4 py-2 rounded-lg text-base border border-white/20">
                        {match.competition}
                    </span>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-6">
                    <div className="bg-white/5 rounded-lg p-6 border border-white/10">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="bg-[#58a6ff]/20 p-2 rounded">
                                <Trophy className="w-6 h-6 text-[#58a6ff]" />
                            </div>
                            <p className="text-[#8b949e] text-sm uppercase tracking-wide">Average Rating</p>
                        </div>
                        <p className="text-4xl text-white">
                            {match.averageRating ? match.averageRating.toFixed(2) : '—'}
                        </p>
                    </div>
                    <div className="bg-white/5 rounded-lg p-6 border border-white/10">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="bg-[#58a6ff]/20 p-2 rounded">
                                <Users className="w-6 h-6 text-[#58a6ff]" />
                            </div>
                            <p className="text-[#8b949e] text-sm uppercase tracking-wide">Total Votes</p>
                        </div>
                        <p className="text-4xl text-white">
                            {match.totalVotes ? match.totalVotes.toLocaleString() : '—'}
                        </p>
                    </div>
                    <div className="bg-white/5 rounded-lg p-6 border border-white/10">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="bg-yellow-500/20 p-2 rounded">
                                <Trophy className="w-6 h-6 text-yellow-400" />
                            </div>
                            <p className="text-[#8b949e] text-sm uppercase tracking-wide">Man of the Match</p>
                        </div>
                        <p className="text-2xl text-white">{match.motm || '—'}</p>
                    </div>
                </div>
            </div>

            {/* Player Ratings */}
            {sortedPlayers.length > 0 && (
                <div className="bg-[#161b22] rounded-lg p-8 border border-[#30363d]">
                    <h3 className="text-2xl text-white mb-6">Player Ratings</h3>
                    <div className="space-y-4">
                        {sortedPlayers.map((player, index) => (
                            <div
                                key={player.name}
                                className="bg-[#0d1117] rounded-lg p-6 border border-[#30363d] hover:border-[#58a6ff] transition-all"
                            >
                                <div className="flex items-center justify-between gap-4 mb-4">
                                    <div className="flex items-center gap-4 flex-1">
                                        <div className="flex items-center gap-3">
                                            {player === topRated && (
                                                <Trophy className="w-5 h-5 text-yellow-400" />
                                            )}
                                            <span className="text-[#8b949e] text-lg w-6">#{index + 1}</span>
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-1">
                                                <h4 className="text-white text-lg">{player.name}</h4>
                                                <span
                                                    className={`${getPositionColor(player.position)} px-2 py-1 rounded text-xs font-semibold`}
                                                >
                                                    {player.position}
                                                </span>
                                                {player.isMotm && (
                                                    <span className="bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded text-xs font-semibold">
                                                        MOTM
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-3xl text-white mb-1">{player.rating.toFixed(1)}</div>
                                    </div>
                                </div>
                                {/* Rating Bar */}
                                <div className="w-full bg-[#30363d] rounded-full h-3 overflow-hidden">
                                    <div
                                        className={`${getRatingColor(player.rating)} h-full rounded-full transition-all duration-500`}
                                        style={{ width: `${(player.rating / 10) * 100}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
