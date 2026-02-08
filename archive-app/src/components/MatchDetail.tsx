import { useState } from 'react';
import { Link } from 'react-router-dom';
import type { Match } from '../types';
import { ArrowLeft, Trophy } from 'lucide-react';

interface MatchDetailProps {
    match: Match;
}

export function MatchDetail({ match }: MatchDetailProps) {
    const BASE = import.meta.env.BASE_URL;

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-GB', {
            weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
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

    const [imgErrors, setImgErrors] = useState<Set<string>>(new Set());
    const handleImgError = (name: string) => {
        setImgErrors((prev) => new Set(prev).add(name));
    };

    const fmtRating = (val: number) => val ? val.toFixed(1) : '—';

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

            {/* Match Header */}
            <div className="bg-gradient-to-r from-[#132257] to-[#1a2d6b] rounded-lg p-8 mb-6 border border-[#30363d]">
                <div className="flex items-center gap-3 mb-3">
                    <span className={`${getResultColor(match.result)} text-white px-4 py-2 rounded-lg text-lg font-semibold`}>
                        {getResultText(match.result)}
                    </span>
                    <span className="text-[#8b949e] text-lg">{match.homeAway}</span>
                </div>
                <h2 className="text-4xl text-white mb-2">
                    Tottenham Hotspur {match.score} {match.opponent}
                </h2>
                <p className="text-[#8b949e] text-lg">{formatDate(match.date)}</p>
                <div className="flex items-center gap-4 mt-4">
                    <span className="bg-white/10 text-white px-4 py-2 rounded-lg text-base border border-white/20">
                        {match.competition}
                    </span>
                    {match.totalVotes > 0 && (
                        <span className="text-[#8b949e] text-base">
                            {match.totalVotes.toLocaleString()} votes
                        </span>
                    )}
                </div>
            </div>

            {/* Match Info Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <InfoCard label="Spurs Score" value={String(match.spursScore)} />
                <InfoCard label={`${match.opponent} Score`} value={String(match.opponentScore)} />
                <InfoCard label="Man of the Match" value={match.motm || '—'} />
                <InfoCard label="Average Rating" value={match.averageRating ? match.averageRating.toFixed(2) : '—'} />
            </div>

            {/* Team / Opponent / Referee Ratings */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                <RatingCard label="Team Rating" mean={match.teamRating.mean} stdDev={match.teamRating.stdDev} getRatingColor={getRatingColor} />
                <RatingCard label="Opponent Rating" mean={match.opponentRating.mean} stdDev={match.opponentRating.stdDev} getRatingColor={getRatingColor} />
                <RatingCard label="Referee Rating" mean={match.refereeRating.mean} stdDev={match.refereeRating.stdDev} getRatingColor={getRatingColor} />
            </div>

            {/* Coach Ratings */}
            {match.coachRatings.name && (
                <div className="bg-[#161b22] rounded-lg p-6 border border-[#30363d] mb-6">
                    <h3 className="text-lg text-white mb-4">
                        Coach: <span className="text-[#d4a843]">{match.coachRatings.name}</span>
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <MiniRating label="Starting XI" mean={match.coachRatings.startingEleven.mean} stdDev={match.coachRatings.startingEleven.stdDev} getRatingColor={getRatingColor} />
                        <MiniRating label="Tactics" mean={match.coachRatings.onFieldTactics.mean} stdDev={match.coachRatings.onFieldTactics.stdDev} getRatingColor={getRatingColor} />
                        <MiniRating label="Substitutions" mean={match.coachRatings.substitutions.mean} stdDev={match.coachRatings.substitutions.stdDev} getRatingColor={getRatingColor} />
                    </div>
                </div>
            )}

            {/* Player Ratings */}
            {sortedPlayers.length > 0 && (
                <div className="bg-[#161b22] rounded-lg p-6 border border-[#30363d]">
                    <h3 className="text-2xl text-white mb-6">Player Ratings</h3>
                    <div className="space-y-3">
                        {sortedPlayers.map((player) => {
                            const showImg = player.imagePath && !imgErrors.has(player.name);
                            return (
                                <div
                                    key={player.name}
                                    className="bg-[#0d1117] rounded-lg p-4 border border-[#30363d] hover:border-[#58a6ff] transition-all"
                                >
                                    <div className="flex items-center gap-4">
                                        {/* Headshot or rank */}
                                        <div className="w-12 h-12 flex-shrink-0 flex items-center justify-center">
                                            {showImg ? (
                                                <img
                                                    src={`${BASE}${player.imagePath}`}
                                                    alt={player.name}
                                                    className="w-12 h-12 rounded-full object-cover bg-[#21262d]"
                                                    onError={() => handleImgError(player.name)}
                                                />
                                            ) : (
                                                <div className="w-12 h-12 rounded-full bg-[#21262d] flex items-center justify-center text-[#8b949e] text-sm font-bold">
                                                    {player.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                                                </div>
                                            )}
                                        </div>
                                        {/* Player info */}
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-1">
                                                {player === topRated && <Trophy className="w-4 h-4 text-yellow-400 flex-shrink-0" />}
                                                <h4 className="text-white text-base truncate">{player.name}</h4>
                                                {player.position && (
                                                    <span className={`${getPositionColor(player.position)} px-2 py-0.5 rounded text-xs font-semibold flex-shrink-0`}>
                                                        {player.position}
                                                    </span>
                                                )}
                                                {player.isMotm && (
                                                    <span className="bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded text-xs font-semibold flex-shrink-0">
                                                        MOTM
                                                    </span>
                                                )}
                                                {!player.isStarter && (
                                                    <span className="text-[#8b949e] text-xs flex-shrink-0">SUB</span>
                                                )}
                                            </div>
                                            {/* Rating bar */}
                                            <div className="w-full bg-[#30363d] rounded-full h-2.5 overflow-hidden">
                                                <div
                                                    className={`${getRatingColor(player.rating)} h-full rounded-full transition-all duration-500`}
                                                    style={{ width: `${(player.rating / 10) * 100}%` }}
                                                />
                                            </div>
                                        </div>
                                        {/* Rating number */}
                                        <div className="text-2xl text-white font-bold flex-shrink-0 w-14 text-right">
                                            {fmtRating(player.rating)}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}

/* Sub-components */

function InfoCard({ label, value }: { label: string; value: string }) {
    return (
        <div className="bg-[#161b22] rounded-lg p-4 border border-[#30363d]">
            <p className="text-[#8b949e] text-xs uppercase tracking-wider mb-1">{label}</p>
            <p className="text-white text-xl font-semibold">{value}</p>
        </div>
    );
}

function RatingCard({ label, mean, stdDev, getRatingColor }: { label: string; mean: number; stdDev: number; getRatingColor: (r: number) => string }) {
    return (
        <div className="bg-[#161b22] rounded-lg p-5 border border-[#30363d]">
            <p className="text-[#8b949e] text-xs uppercase tracking-wider mb-2">{label}</p>
            <div className="flex items-end gap-2 mb-2">
                <span className="text-3xl text-white font-bold">{mean ? mean.toFixed(1) : '—'}</span>
                {stdDev > 0 && <span className="text-[#8b949e] text-sm mb-1">± {stdDev.toFixed(1)}</span>}
            </div>
            {mean > 0 && (
                <div className="w-full bg-[#30363d] rounded-full h-2.5 overflow-hidden">
                    <div
                        className={`${getRatingColor(mean)} h-full rounded-full`}
                        style={{ width: `${(mean / 10) * 100}%` }}
                    />
                </div>
            )}
        </div>
    );
}

function MiniRating({ label, mean, stdDev, getRatingColor }: { label: string; mean: number; stdDev: number; getRatingColor: (r: number) => string }) {
    return (
        <div className="bg-[#0d1117] rounded-lg p-4 border border-[#30363d]">
            <p className="text-[#8b949e] text-xs uppercase tracking-wider mb-1">{label}</p>
            <div className="flex items-end gap-2 mb-2">
                <span className="text-2xl text-white font-bold">{mean ? mean.toFixed(1) : '—'}</span>
                {stdDev > 0 && <span className="text-[#8b949e] text-sm mb-0.5">± {stdDev.toFixed(1)}</span>}
            </div>
            {mean > 0 && (
                <div className="w-full bg-[#30363d] rounded-full h-2 overflow-hidden">
                    <div
                        className={`${getRatingColor(mean)} h-full rounded-full`}
                        style={{ width: `${(mean / 10) * 100}%` }}
                    />
                </div>
            )}
        </div>
    );
}
