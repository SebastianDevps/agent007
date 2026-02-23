"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const vitest_1 = require("vitest");
const game_engine_1 = require("../game/game.engine");
// ---------------------------------------------------------------------------
// Test helper
// ---------------------------------------------------------------------------
function makePlayer(id, name, overrides) {
    return {
        id,
        name,
        role: null,
        isAlive: true,
        sessionToken: '',
        ...overrides,
    };
}
function makeRoom(overrides) {
    return {
        code: 'TEST01',
        hostId: 'host-1',
        phase: 'lobby',
        players: new Map([['host-1', makePlayer('host-1', 'Host')]]),
        config: { impostorCount: 1, rounds: 3, categoryId: 'cat-1', categoryName: 'Test' },
        word: 'perro',
        referenceWord: 'lobo',
        currentRound: 1,
        turnOrder: ['host-1'],
        currentTurnIndex: 0,
        turnDirection: 'right',
        clues: new Map(),
        votes: new Map(),
        eliminatedIds: new Set(),
        readyPlayers: new Set(),
        readyTimeout: null,
        ...overrides,
    };
}
/** Build a room with N players, all alive, roles unset. */
function makeRoomWithPlayers(count, impostorCount = 1, rounds = 3) {
    const players = new Map();
    for (let i = 1; i <= count; i++) {
        const id = `player-${i}`;
        players.set(id, makePlayer(id, `Player ${i}`));
    }
    return makeRoom({
        hostId: 'player-1',
        players,
        config: { impostorCount, rounds, categoryId: 'cat-1', categoryName: 'Test' },
        turnOrder: Array.from(players.keys()),
    });
}
// ---------------------------------------------------------------------------
// assignRoles
// ---------------------------------------------------------------------------
(0, vitest_1.describe)('assignRoles', () => {
    (0, vitest_1.beforeEach)(() => {
        // Reset any Math.random mock after each test
        vitest_1.vi.restoreAllMocks();
    });
    (0, vitest_1.it)('assigns exactly N impostors according to config', () => {
        const room = makeRoomWithPlayers(6, 2);
        (0, game_engine_1.assignRoles)(room);
        const impostors = Array.from(room.players.values()).filter((p) => p.role === 'impostor');
        (0, vitest_1.expect)(impostors).toHaveLength(2);
    });
    (0, vitest_1.it)('assigns civil role to all non-impostor players', () => {
        const room = makeRoomWithPlayers(6, 2);
        (0, game_engine_1.assignRoles)(room);
        const civiles = Array.from(room.players.values()).filter((p) => p.role === 'civil');
        (0, vitest_1.expect)(civiles).toHaveLength(4);
    });
    (0, vitest_1.it)('assigns every player a role (no null roles after call)', () => {
        const room = makeRoomWithPlayers(5, 1);
        (0, game_engine_1.assignRoles)(room);
        for (const player of room.players.values()) {
            (0, vitest_1.expect)(player.role).not.toBeNull();
        }
    });
    (0, vitest_1.it)('shuffles turnOrder and resets currentTurnIndex to 0', () => {
        const room = makeRoomWithPlayers(5, 1);
        (0, game_engine_1.assignRoles)(room);
        // turnOrder must contain all player IDs (same set, potentially different order)
        const originalIds = Array.from(room.players.keys()).sort();
        (0, vitest_1.expect)(room.turnOrder.slice().sort()).toEqual(originalIds);
        (0, vitest_1.expect)(room.currentTurnIndex).toBe(0);
    });
    (0, vitest_1.it)('works correctly with minimum 2 players (1 impostor, 1 civil)', () => {
        const room = makeRoomWithPlayers(2, 1);
        (0, game_engine_1.assignRoles)(room);
        const roles = Array.from(room.players.values()).map((p) => p.role);
        (0, vitest_1.expect)(roles).toContain('impostor');
        (0, vitest_1.expect)(roles).toContain('civil');
    });
    (0, vitest_1.it)('does not assign more impostors than players-1 even if config requests it', () => {
        // Config says 5 impostors but there are only 3 players → max allowed = 2
        const room = makeRoomWithPlayers(3, 5);
        (0, game_engine_1.assignRoles)(room);
        const impostors = Array.from(room.players.values()).filter((p) => p.role === 'impostor');
        // Should be capped at playerCount - 1 = 2
        (0, vitest_1.expect)(impostors.length).toBeLessThanOrEqual(2);
        // At least 1 civil must always exist
        const civiles = Array.from(room.players.values()).filter((p) => p.role === 'civil');
        (0, vitest_1.expect)(civiles.length).toBeGreaterThanOrEqual(1);
    });
    (0, vitest_1.it)('caps impostorCount at playerCount-1 exactly for edge config', () => {
        // 4 players, config asks for 10 → should cap at 3
        const room = makeRoomWithPlayers(4, 10);
        (0, game_engine_1.assignRoles)(room);
        const impostors = Array.from(room.players.values()).filter((p) => p.role === 'impostor');
        (0, vitest_1.expect)(impostors).toHaveLength(3);
    });
    (0, vitest_1.it)('marks all players as isAlive=true after assignment', () => {
        const room = makeRoomWithPlayers(4, 1);
        // Simulate a player that was previously dead
        const firstPlayer = room.players.values().next().value;
        firstPlayer.isAlive = false;
        (0, game_engine_1.assignRoles)(room);
        for (const player of room.players.values()) {
            (0, vitest_1.expect)(player.isAlive).toBe(true);
        }
    });
    (0, vitest_1.it)('throws when room has no config', () => {
        const room = makeRoom({ config: null });
        (0, vitest_1.expect)(() => (0, game_engine_1.assignRoles)(room)).toThrow('Cannot assign roles without game config');
    });
    (0, vitest_1.it)('produces different turnOrder arrangements across multiple calls (statistical)', () => {
        // Run 20 times on a 5-player room and verify at least one shuffled result differs
        const ordersSet = new Set();
        for (let i = 0; i < 20; i++) {
            const room = makeRoomWithPlayers(5, 1);
            (0, game_engine_1.assignRoles)(room);
            ordersSet.add(room.turnOrder.join(','));
        }
        // With 5 players, 5! = 120 possible orders; 20 runs should produce >1 unique order
        (0, vitest_1.expect)(ordersSet.size).toBeGreaterThan(1);
    });
});
// ---------------------------------------------------------------------------
// getNextTurnIndex
// ---------------------------------------------------------------------------
(0, vitest_1.describe)('getNextTurnIndex', () => {
    (0, vitest_1.it)('advances to the right (increment) by default', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1')],
                ['p2', makePlayer('p2', 'P2')],
                ['p3', makePlayer('p3', 'P3')],
            ]),
            turnOrder: ['p1', 'p2', 'p3'],
            currentTurnIndex: 0,
            turnDirection: 'right',
            eliminatedIds: new Set(),
        });
        (0, vitest_1.expect)((0, game_engine_1.getNextTurnIndex)(room)).toBe(1);
    });
    (0, vitest_1.it)('advances to the left (decrement) when direction is left', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1')],
                ['p2', makePlayer('p2', 'P2')],
                ['p3', makePlayer('p3', 'P3')],
            ]),
            turnOrder: ['p1', 'p2', 'p3'],
            currentTurnIndex: 0,
            turnDirection: 'left',
            eliminatedIds: new Set(),
        });
        // From index 0 going left wraps to index 2
        (0, vitest_1.expect)((0, game_engine_1.getNextTurnIndex)(room)).toBe(2);
    });
    (0, vitest_1.it)('wraps around to index 0 when advancing right past the last player', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1')],
                ['p2', makePlayer('p2', 'P2')],
                ['p3', makePlayer('p3', 'P3')],
            ]),
            turnOrder: ['p1', 'p2', 'p3'],
            currentTurnIndex: 2,
            turnDirection: 'right',
            eliminatedIds: new Set(),
        });
        (0, vitest_1.expect)((0, game_engine_1.getNextTurnIndex)(room)).toBe(0);
    });
    (0, vitest_1.it)('wraps around to last index when advancing left from index 0', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1')],
                ['p2', makePlayer('p2', 'P2')],
                ['p3', makePlayer('p3', 'P3')],
            ]),
            turnOrder: ['p1', 'p2', 'p3'],
            currentTurnIndex: 0,
            turnDirection: 'left',
            eliminatedIds: new Set(),
        });
        (0, vitest_1.expect)((0, game_engine_1.getNextTurnIndex)(room)).toBe(2);
    });
    (0, vitest_1.it)('skips players that are in eliminatedIds when going right', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1')],
                ['p2', makePlayer('p2', 'P2', { isAlive: false })],
                ['p3', makePlayer('p3', 'P3')],
            ]),
            turnOrder: ['p1', 'p2', 'p3'],
            currentTurnIndex: 0,
            turnDirection: 'right',
            eliminatedIds: new Set(['p2']),
        });
        // p2 is eliminated → should skip to p3 at index 2
        (0, vitest_1.expect)((0, game_engine_1.getNextTurnIndex)(room)).toBe(2);
    });
    (0, vitest_1.it)('skips players that have isAlive=false when going right', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1')],
                ['p2', makePlayer('p2', 'P2', { isAlive: false })],
                ['p3', makePlayer('p3', 'P3')],
            ]),
            turnOrder: ['p1', 'p2', 'p3'],
            currentTurnIndex: 0,
            turnDirection: 'right',
            eliminatedIds: new Set(),
        });
        // p2.isAlive is false → skip to p3
        (0, vitest_1.expect)((0, game_engine_1.getNextTurnIndex)(room)).toBe(2);
    });
    (0, vitest_1.it)('skips multiple consecutive eliminated players', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1')],
                ['p2', makePlayer('p2', 'P2', { isAlive: false })],
                ['p3', makePlayer('p3', 'P3', { isAlive: false })],
                ['p4', makePlayer('p4', 'P4')],
            ]),
            turnOrder: ['p1', 'p2', 'p3', 'p4'],
            currentTurnIndex: 0,
            turnDirection: 'right',
            eliminatedIds: new Set(['p2', 'p3']),
        });
        (0, vitest_1.expect)((0, game_engine_1.getNextTurnIndex)(room)).toBe(3);
    });
    (0, vitest_1.it)('returns currentTurnIndex when all players are eliminated (no valid next)', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { isAlive: false })],
                ['p2', makePlayer('p2', 'P2', { isAlive: false })],
            ]),
            turnOrder: ['p1', 'p2'],
            currentTurnIndex: 0,
            turnDirection: 'right',
            eliminatedIds: new Set(['p1', 'p2']),
        });
        (0, vitest_1.expect)((0, game_engine_1.getNextTurnIndex)(room)).toBe(0);
    });
    (0, vitest_1.it)('skips eliminated players going left', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1')],
                ['p2', makePlayer('p2', 'P2', { isAlive: false })],
                ['p3', makePlayer('p3', 'P3')],
            ]),
            turnOrder: ['p1', 'p2', 'p3'],
            currentTurnIndex: 2,
            turnDirection: 'left',
            eliminatedIds: new Set(['p2']),
        });
        // Going left from p3 (index 2): p2 is eliminated → skip to p1 (index 0)
        (0, vitest_1.expect)((0, game_engine_1.getNextTurnIndex)(room)).toBe(0);
    });
});
// ---------------------------------------------------------------------------
// resolveVotes
// ---------------------------------------------------------------------------
(0, vitest_1.describe)('resolveVotes', () => {
    (0, vitest_1.it)('eliminates the player with the most votes', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
                ['p2', makePlayer('p2', 'P2', { role: 'civil' })],
                ['p3', makePlayer('p3', 'P3', { role: 'impostor' })],
            ]),
            // p1 and p2 vote for p3, p3 votes for p1
            votes: new Map([
                ['p1', 'p3'],
                ['p2', 'p3'],
                ['p3', 'p1'],
            ]),
            eliminatedIds: new Set(),
        });
        const result = (0, game_engine_1.resolveVotes)(room);
        (0, vitest_1.expect)(result.eliminatedId).toBe('p3');
        (0, vitest_1.expect)(result.eliminatedName).toBe('P3');
        (0, vitest_1.expect)(result.eliminatedRole).toBe('impostor');
    });
    (0, vitest_1.it)('marks the eliminated player as isAlive=false', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
                ['p2', makePlayer('p2', 'P2', { role: 'civil' })],
                ['p3', makePlayer('p3', 'P3', { role: 'impostor' })],
            ]),
            votes: new Map([['p1', 'p3'], ['p2', 'p3']]),
            eliminatedIds: new Set(),
        });
        (0, game_engine_1.resolveVotes)(room);
        (0, vitest_1.expect)(room.players.get('p3').isAlive).toBe(false);
    });
    (0, vitest_1.it)('adds the eliminated player to room.eliminatedIds', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
            ]),
            votes: new Map([['p1', 'p2']]),
            eliminatedIds: new Set(),
        });
        (0, game_engine_1.resolveVotes)(room);
        (0, vitest_1.expect)(room.eliminatedIds.has('p2')).toBe(true);
    });
    (0, vitest_1.it)('returns winner=civiles when the last impostor is eliminated', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
            ]),
            votes: new Map([['p1', 'p2']]),
            eliminatedIds: new Set(),
        });
        const result = (0, game_engine_1.resolveVotes)(room);
        (0, vitest_1.expect)(result.winner).toBe('civiles');
    });
    (0, vitest_1.it)('does not set winner when a civil is eliminated', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
                ['p3', makePlayer('p3', 'P3', { role: 'civil' })],
            ]),
            votes: new Map([['p1', 'p3'], ['p2', 'p3']]),
            eliminatedIds: new Set(),
        });
        const result = (0, game_engine_1.resolveVotes)(room);
        (0, vitest_1.expect)(result.winner).toBeUndefined();
    });
    (0, vitest_1.it)('returns no winner when an impostor is eliminated but other impostors survive', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
                ['p3', makePlayer('p3', 'P3', { role: 'impostor' })],
            ]),
            votes: new Map([['p1', 'p2']]),
            eliminatedIds: new Set(),
        });
        const result = (0, game_engine_1.resolveVotes)(room);
        (0, vitest_1.expect)(result.winner).toBeUndefined();
    });
    (0, vitest_1.it)('returns null eliminatedId on a tie (two players with equal votes)', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
                ['p3', makePlayer('p3', 'P3', { role: 'civil' })],
            ]),
            // p1 votes p2, p2 votes p1 → tie between p1 and p2
            votes: new Map([
                ['p1', 'p2'],
                ['p2', 'p1'],
            ]),
            eliminatedIds: new Set(),
        });
        const result = (0, game_engine_1.resolveVotes)(room);
        (0, vitest_1.expect)(result.eliminatedId).toBeNull();
        (0, vitest_1.expect)(result.eliminatedName).toBeNull();
        (0, vitest_1.expect)(result.eliminatedRole).toBeNull();
    });
    (0, vitest_1.it)('does not mark anyone as eliminated on a tie', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
            ]),
            votes: new Map([['p1', 'p2'], ['p2', 'p1']]),
            eliminatedIds: new Set(),
        });
        (0, game_engine_1.resolveVotes)(room);
        (0, vitest_1.expect)(room.eliminatedIds.size).toBe(0);
        (0, vitest_1.expect)(room.players.get('p1').isAlive).toBe(true);
        (0, vitest_1.expect)(room.players.get('p2').isAlive).toBe(true);
    });
    (0, vitest_1.it)('returns correct votes record mapping voterId→targetId', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
            ]),
            votes: new Map([['p1', 'p2'], ['p2', 'p1']]),
            eliminatedIds: new Set(),
        });
        const result = (0, game_engine_1.resolveVotes)(room);
        (0, vitest_1.expect)(result.votes).toEqual({ p1: 'p2', p2: 'p1' });
    });
    (0, vitest_1.it)('handles empty votes map (no votes → tie at 0)', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
            ]),
            votes: new Map(),
            eliminatedIds: new Set(),
        });
        const result = (0, game_engine_1.resolveVotes)(room);
        // No candidates → nobody eliminated
        (0, vitest_1.expect)(result.eliminatedId).toBeNull();
        (0, vitest_1.expect)(result.votes).toEqual({});
    });
});
// ---------------------------------------------------------------------------
// checkVictory
// ---------------------------------------------------------------------------
(0, vitest_1.describe)('checkVictory', () => {
    (0, vitest_1.it)("returns 'civiles' when all impostors are eliminated", () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: false })],
            ]),
            config: { impostorCount: 1, rounds: 3, categoryId: 'cat-1', categoryName: 'Test' },
            currentRound: 1,
        });
        (0, vitest_1.expect)((0, game_engine_1.checkVictory)(room)).toBe('civiles');
    });
    (0, vitest_1.it)("returns 'impostores' when all rounds are exhausted and impostors survive", () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: true })],
            ]),
            config: { impostorCount: 1, rounds: 3, categoryId: 'cat-1', categoryName: 'Test' },
            currentRound: 3, // at final round
        });
        (0, vitest_1.expect)((0, game_engine_1.checkVictory)(room)).toBe('impostores');
    });
    (0, vitest_1.it)('returns null when impostors alive and rounds remain', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: true })],
            ]),
            config: { impostorCount: 1, rounds: 3, categoryId: 'cat-1', categoryName: 'Test' },
            currentRound: 1,
        });
        (0, vitest_1.expect)((0, game_engine_1.checkVictory)(room)).toBeNull();
    });
    (0, vitest_1.it)("returns 'civiles' even if rounds are exhausted when no impostors are alive", () => {
        // civiles win condition takes priority
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: false })],
            ]),
            config: { impostorCount: 1, rounds: 3, categoryId: 'cat-1', categoryName: 'Test' },
            currentRound: 3,
        });
        (0, vitest_1.expect)((0, game_engine_1.checkVictory)(room)).toBe('civiles');
    });
    (0, vitest_1.it)('returns null when currentRound is below total rounds and impostors are alive', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: true })],
                ['p3', makePlayer('p3', 'P3', { role: 'civil', isAlive: true })],
            ]),
            config: { impostorCount: 1, rounds: 5, categoryId: 'cat-1', categoryName: 'Test' },
            currentRound: 2,
        });
        (0, vitest_1.expect)((0, game_engine_1.checkVictory)(room)).toBeNull();
    });
    (0, vitest_1.it)('returns null when no config is present and impostors are alive', () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: true })],
            ]),
            config: null,
            currentRound: 99,
        });
        // No config → cannot determine round victory → returns null
        (0, vitest_1.expect)((0, game_engine_1.checkVictory)(room)).toBeNull();
    });
    (0, vitest_1.it)("returns 'impostores' exactly at currentRound === config.rounds", () => {
        const room = makeRoom({
            players: new Map([
                ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
                ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: true })],
            ]),
            config: { impostorCount: 1, rounds: 5, categoryId: 'cat-1', categoryName: 'Test' },
            currentRound: 5,
        });
        (0, vitest_1.expect)((0, game_engine_1.checkVictory)(room)).toBe('impostores');
    });
});
