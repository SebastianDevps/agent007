"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.assignRoles = assignRoles;
exports.getNextTurnIndex = getNextTurnIndex;
exports.resolveVotes = resolveVotes;
exports.checkVictory = checkVictory;
/**
 * Shuffle an array in-place using Fisher-Yates algorithm.
 */
function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}
/**
 * Assign roles randomly to all players in the room.
 * The number of impostors is determined by config.impostorCount.
 * Also shuffles turnOrder with alive player IDs.
 */
function assignRoles(room) {
    const config = room.config;
    if (!config) {
        throw new Error('Cannot assign roles without game config');
    }
    const playerIds = Array.from(room.players.keys());
    const shuffled = shuffle([...playerIds]);
    const impostorCount = Math.min(config.impostorCount, playerIds.length - 1);
    for (let i = 0; i < shuffled.length; i++) {
        const player = room.players.get(shuffled[i]);
        if (!player)
            continue;
        player.role = i < impostorCount ? 'impostor' : 'civil';
        player.isAlive = true;
    }
    room.turnOrder = shuffle([...playerIds]);
    room.currentTurnIndex = 0;
}
/**
 * Get the next turn index, skipping eliminated players.
 * Respects turnDirection (left = decrement, right = increment).
 */
function getNextTurnIndex(room) {
    const order = room.turnOrder;
    const direction = room.turnDirection === 'right' ? 1 : -1;
    let index = room.currentTurnIndex;
    for (let attempts = 0; attempts < order.length; attempts++) {
        index = (index + direction + order.length) % order.length;
        const playerId = order[index];
        const player = room.players.get(playerId);
        if (player && player.isAlive && !room.eliminatedIds.has(playerId)) {
            return index;
        }
    }
    return room.currentTurnIndex;
}
/**
 * Resolve votes for the current round.
 * The player with the most votes is eliminated.
 * In case of a tie, nobody is eliminated.
 * If an impostor is eliminated, civiles win immediately.
 */
function resolveVotes(room) {
    const votesRecord = {};
    const tally = new Map();
    for (const [voterId, targetId] of room.votes.entries()) {
        votesRecord[voterId] = targetId;
        tally.set(targetId, (tally.get(targetId) ?? 0) + 1);
    }
    // Find player(s) with most votes
    let maxVotes = 0;
    let candidates = [];
    for (const [playerId, count] of tally.entries()) {
        if (count > maxVotes) {
            maxVotes = count;
            candidates = [playerId];
        }
        else if (count === maxVotes) {
            candidates.push(playerId);
        }
    }
    // Tie: nobody eliminated
    if (candidates.length !== 1) {
        return {
            eliminatedId: null,
            eliminatedName: null,
            eliminatedRole: null,
            votes: votesRecord,
        };
    }
    const eliminatedId = candidates[0];
    const eliminated = room.players.get(eliminatedId);
    if (!eliminated) {
        return {
            eliminatedId: null,
            eliminatedName: null,
            eliminatedRole: null,
            votes: votesRecord,
        };
    }
    // Mark player as eliminated
    eliminated.isAlive = false;
    room.eliminatedIds.add(eliminatedId);
    const result = {
        eliminatedId,
        eliminatedName: eliminated.name,
        eliminatedRole: eliminated.role,
        votes: votesRecord,
    };
    // If impostor was eliminated, civiles win immediately
    if (eliminated.role === 'impostor') {
        const remainingImpostors = Array.from(room.players.values()).filter((p) => p.role === 'impostor' && p.isAlive);
        if (remainingImpostors.length === 0) {
            result.winner = 'civiles';
        }
    }
    return result;
}
/**
 * Check if there is a winner.
 * - 'civiles' if no impostors are alive
 * - 'impostores' if all rounds are done and impostors survive
 * - null if the game continues
 */
function checkVictory(room) {
    const alivePlayers = Array.from(room.players.values()).filter((p) => p.isAlive);
    const aliveImpostors = alivePlayers.filter((p) => p.role === 'impostor');
    // All impostors eliminated
    if (aliveImpostors.length === 0) {
        return 'civiles';
    }
    // All rounds completed and impostors survived
    const config = room.config;
    if (config && room.currentRound >= config.rounds) {
        return 'impostores';
    }
    return null;
}
