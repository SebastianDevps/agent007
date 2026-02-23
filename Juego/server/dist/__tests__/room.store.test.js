"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const vitest_1 = require("vitest");
const room_store_1 = require("../rooms/room.store");
// ---------------------------------------------------------------------------
// Test helpers
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
/**
 * The room store uses a module-level Map that persists between tests.
 * We clear it before each test by deleting every room that was created.
 * We track created codes via a local array to avoid coupling to internals.
 */
let createdCodes = [];
(0, vitest_1.beforeEach)(() => {
    for (const code of createdCodes) {
        (0, room_store_1.deleteRoom)(code);
    }
    createdCodes = [];
});
function trackRoom(room) {
    createdCodes.push(room.code);
    return room;
}
// ---------------------------------------------------------------------------
// createRoom
// ---------------------------------------------------------------------------
(0, vitest_1.describe)('createRoom', () => {
    (0, vitest_1.it)('creates a room with a 6-character uppercase code', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, vitest_1.expect)(room.code).toHaveLength(6);
        (0, vitest_1.expect)(room.code).toBe(room.code.toUpperCase());
    });
    (0, vitest_1.it)('creates rooms with unique codes across multiple calls', () => {
        const codes = new Set();
        for (let i = 0; i < 20; i++) {
            const room = trackRoom((0, room_store_1.createRoom)(`host-${i}`, `Host ${i}`));
            codes.add(room.code);
        }
        // All 20 rooms should have distinct codes
        (0, vitest_1.expect)(codes.size).toBe(20);
    });
    (0, vitest_1.it)('sets the correct hostId', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-42', 'Bob'));
        (0, vitest_1.expect)(room.hostId).toBe('host-42');
    });
    (0, vitest_1.it)('creates room in lobby phase', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, vitest_1.expect)(room.phase).toBe('lobby');
    });
    (0, vitest_1.it)('adds the host as the sole initial player', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, vitest_1.expect)(room.players.size).toBe(1);
        (0, vitest_1.expect)(room.players.has('host-1')).toBe(true);
    });
    (0, vitest_1.it)('host player has correct name and default values', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        const host = room.players.get('host-1');
        (0, vitest_1.expect)(host.name).toBe('Alice');
        (0, vitest_1.expect)(host.role).toBeNull();
        (0, vitest_1.expect)(host.isAlive).toBe(true);
    });
    (0, vitest_1.it)('initializes config as null', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, vitest_1.expect)(room.config).toBeNull();
    });
    (0, vitest_1.it)('stores the room so it can be retrieved with getRoom', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        const retrieved = (0, room_store_1.getRoom)(room.code);
        (0, vitest_1.expect)(retrieved).toBe(room);
    });
});
// ---------------------------------------------------------------------------
// addPlayer
// ---------------------------------------------------------------------------
(0, vitest_1.describe)('addPlayer', () => {
    (0, vitest_1.it)('adds a player to an existing room', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        const player = makePlayer('player-2', 'Bob');
        const success = (0, room_store_1.addPlayer)(room.code, player);
        (0, vitest_1.expect)(success).toBe(true);
        (0, vitest_1.expect)(room.players.has('player-2')).toBe(true);
        (0, vitest_1.expect)(room.players.get('player-2').name).toBe('Bob');
    });
    (0, vitest_1.it)('returns false for a non-existent room code', () => {
        const player = makePlayer('p1', 'Stranger');
        const result = (0, room_store_1.addPlayer)('NOROOM', player);
        (0, vitest_1.expect)(result).toBe(false);
    });
    (0, vitest_1.it)('returns false when the room already has 10 players (MAX_PLAYERS)', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Host'));
        // Fill to 10 (host is player 1, add 9 more)
        for (let i = 2; i <= 10; i++) {
            (0, room_store_1.addPlayer)(room.code, makePlayer(`p${i}`, `Player ${i}`));
        }
        (0, vitest_1.expect)(room.players.size).toBe(10);
        const eleventh = makePlayer('p11', 'One Too Many');
        const result = (0, room_store_1.addPlayer)(room.code, eleventh);
        (0, vitest_1.expect)(result).toBe(false);
        (0, vitest_1.expect)(room.players.size).toBe(10);
    });
    (0, vitest_1.it)('accepts the 10th player exactly (boundary)', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Host'));
        for (let i = 2; i <= 9; i++) {
            (0, room_store_1.addPlayer)(room.code, makePlayer(`p${i}`, `Player ${i}`));
        }
        (0, vitest_1.expect)(room.players.size).toBe(9);
        const tenth = makePlayer('p10', 'Player 10');
        const result = (0, room_store_1.addPlayer)(room.code, tenth);
        (0, vitest_1.expect)(result).toBe(true);
        (0, vitest_1.expect)(room.players.size).toBe(10);
    });
    (0, vitest_1.it)('preserves all player fields after adding', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        const player = makePlayer('p2', 'Carlos', { role: 'civil', isAlive: false });
        (0, room_store_1.addPlayer)(room.code, player);
        const stored = room.players.get('p2');
        (0, vitest_1.expect)(stored.id).toBe('p2');
        (0, vitest_1.expect)(stored.name).toBe('Carlos');
        (0, vitest_1.expect)(stored.role).toBe('civil');
        (0, vitest_1.expect)(stored.isAlive).toBe(false);
    });
});
// ---------------------------------------------------------------------------
// removePlayer
// ---------------------------------------------------------------------------
(0, vitest_1.describe)('removePlayer', () => {
    (0, vitest_1.it)('removes an existing player from the room', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, room_store_1.addPlayer)(room.code, makePlayer('p2', 'Bob'));
        (0, room_store_1.removePlayer)(room.code, 'p2');
        (0, vitest_1.expect)(room.players.has('p2')).toBe(false);
        (0, vitest_1.expect)(room.players.size).toBe(1);
    });
    (0, vitest_1.it)('does nothing when the player does not exist in the room', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, vitest_1.expect)(() => (0, room_store_1.removePlayer)(room.code, 'ghost-player')).not.toThrow();
        (0, vitest_1.expect)(room.players.size).toBe(1);
    });
    (0, vitest_1.it)('does nothing when the room code does not exist', () => {
        (0, vitest_1.expect)(() => (0, room_store_1.removePlayer)('NOROOM', 'p1')).not.toThrow();
    });
    (0, vitest_1.it)('can remove the host player', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, room_store_1.removePlayer)(room.code, 'host-1');
        (0, vitest_1.expect)(room.players.has('host-1')).toBe(false);
        (0, vitest_1.expect)(room.players.size).toBe(0);
    });
});
// ---------------------------------------------------------------------------
// deleteRoom
// ---------------------------------------------------------------------------
(0, vitest_1.describe)('deleteRoom', () => {
    (0, vitest_1.it)('deletes a room so getRoom returns undefined', () => {
        const room = (0, room_store_1.createRoom)('host-1', 'Alice');
        const code = room.code;
        (0, room_store_1.deleteRoom)(code);
        (0, vitest_1.expect)((0, room_store_1.getRoom)(code)).toBeUndefined();
    });
    (0, vitest_1.it)('does nothing when the room code does not exist', () => {
        (0, vitest_1.expect)(() => (0, room_store_1.deleteRoom)('GHOST1')).not.toThrow();
    });
    (0, vitest_1.it)('only deletes the targeted room, leaving others intact', () => {
        const room1 = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        const room2 = trackRoom((0, room_store_1.createRoom)('host-2', 'Bob'));
        (0, room_store_1.deleteRoom)(room1.code);
        // Remove room1 from tracking since we already deleted it
        createdCodes = createdCodes.filter((c) => c !== room1.code);
        (0, vitest_1.expect)((0, room_store_1.getRoom)(room1.code)).toBeUndefined();
        (0, vitest_1.expect)((0, room_store_1.getRoom)(room2.code)).toBeDefined();
    });
});
// ---------------------------------------------------------------------------
// findRoomByPlayerId
// ---------------------------------------------------------------------------
(0, vitest_1.describe)('findRoomByPlayerId', () => {
    (0, vitest_1.it)('returns the room containing the given player', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, room_store_1.addPlayer)(room.code, makePlayer('p2', 'Bob'));
        const found = (0, room_store_1.findRoomByPlayerId)('p2');
        (0, vitest_1.expect)(found).toBeDefined();
        (0, vitest_1.expect)(found.code).toBe(room.code);
    });
    (0, vitest_1.it)('finds the host player in their room', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        const found = (0, room_store_1.findRoomByPlayerId)('host-1');
        (0, vitest_1.expect)(found).toBeDefined();
        (0, vitest_1.expect)(found.code).toBe(room.code);
    });
    (0, vitest_1.it)('returns undefined when the player is in no room', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        // Ensure the player is not in any room
        void room;
        const found = (0, room_store_1.findRoomByPlayerId)('completely-unknown-player');
        (0, vitest_1.expect)(found).toBeUndefined();
    });
    (0, vitest_1.it)('returns the correct room when multiple rooms exist', () => {
        const room1 = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        const room2 = trackRoom((0, room_store_1.createRoom)('host-2', 'Bob'));
        (0, room_store_1.addPlayer)(room2.code, makePlayer('p3', 'Carol'));
        const found = (0, room_store_1.findRoomByPlayerId)('p3');
        (0, vitest_1.expect)(found.code).toBe(room2.code);
        (0, vitest_1.expect)(found.code).not.toBe(room1.code);
    });
    (0, vitest_1.it)('returns undefined after the player is removed from the room', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, room_store_1.addPlayer)(room.code, makePlayer('p2', 'Bob'));
        (0, room_store_1.removePlayer)(room.code, 'p2');
        const found = (0, room_store_1.findRoomByPlayerId)('p2');
        (0, vitest_1.expect)(found).toBeUndefined();
    });
});
// ---------------------------------------------------------------------------
// serializePlayers
// ---------------------------------------------------------------------------
(0, vitest_1.describe)('serializePlayers', () => {
    (0, vitest_1.it)('returns an array with one entry per player', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, room_store_1.addPlayer)(room.code, makePlayer('p2', 'Bob'));
        const serialized = (0, room_store_1.serializePlayers)(room);
        (0, vitest_1.expect)(serialized).toHaveLength(2);
    });
    (0, vitest_1.it)('marks isHost=true only for the host', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, room_store_1.addPlayer)(room.code, makePlayer('p2', 'Bob'));
        const serialized = (0, room_store_1.serializePlayers)(room);
        const hostEntry = serialized.find((p) => p.id === 'host-1');
        const otherEntry = serialized.find((p) => p.id === 'p2');
        (0, vitest_1.expect)(hostEntry.isHost).toBe(true);
        (0, vitest_1.expect)(otherEntry.isHost).toBe(false);
    });
    (0, vitest_1.it)('marks isHost=false for all non-host players', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        for (let i = 2; i <= 5; i++) {
            (0, room_store_1.addPlayer)(room.code, makePlayer(`p${i}`, `Player ${i}`));
        }
        const serialized = (0, room_store_1.serializePlayers)(room);
        const nonHosts = serialized.filter((p) => p.id !== 'host-1');
        for (const entry of nonHosts) {
            (0, vitest_1.expect)(entry.isHost).toBe(false);
        }
    });
    (0, vitest_1.it)('marks isEliminated=true for players in eliminatedIds', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, room_store_1.addPlayer)(room.code, makePlayer('p2', 'Bob'));
        room.eliminatedIds.add('p2');
        const serialized = (0, room_store_1.serializePlayers)(room);
        const p2 = serialized.find((p) => p.id === 'p2');
        (0, vitest_1.expect)(p2.isEliminated).toBe(true);
    });
    (0, vitest_1.it)('marks isEliminated=false for players not in eliminatedIds', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, room_store_1.addPlayer)(room.code, makePlayer('p2', 'Bob'));
        const serialized = (0, room_store_1.serializePlayers)(room);
        const p2 = serialized.find((p) => p.id === 'p2');
        (0, vitest_1.expect)(p2.isEliminated).toBe(false);
    });
    (0, vitest_1.it)('includes correct isAlive value for each player', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, room_store_1.addPlayer)(room.code, makePlayer('p2', 'Bob', { isAlive: false }));
        const serialized = (0, room_store_1.serializePlayers)(room);
        const p2 = serialized.find((p) => p.id === 'p2');
        (0, vitest_1.expect)(p2.isAlive).toBe(false);
    });
    (0, vitest_1.it)('includes correct name for each serialized player', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, room_store_1.addPlayer)(room.code, makePlayer('p2', 'Bob'));
        const serialized = (0, room_store_1.serializePlayers)(room);
        const names = serialized.map((p) => p.name).sort();
        (0, vitest_1.expect)(names).toEqual(['Alice', 'Bob']);
    });
    (0, vitest_1.it)('does not expose role in serialized output', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        const player = makePlayer('p2', 'Bob', { role: 'impostor' });
        (0, room_store_1.addPlayer)(room.code, player);
        const serialized = (0, room_store_1.serializePlayers)(room);
        for (const entry of serialized) {
            (0, vitest_1.expect)(entry).not.toHaveProperty('role');
        }
    });
    (0, vitest_1.it)('returns empty array when room has no players', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        room.players.clear();
        const serialized = (0, room_store_1.serializePlayers)(room);
        (0, vitest_1.expect)(serialized).toEqual([]);
    });
    (0, vitest_1.it)('correctly marks multiple eliminated players', () => {
        const room = trackRoom((0, room_store_1.createRoom)('host-1', 'Alice'));
        (0, room_store_1.addPlayer)(room.code, makePlayer('p2', 'Bob'));
        (0, room_store_1.addPlayer)(room.code, makePlayer('p3', 'Carol'));
        room.eliminatedIds.add('host-1');
        room.eliminatedIds.add('p3');
        const serialized = (0, room_store_1.serializePlayers)(room);
        const byId = Object.fromEntries(serialized.map((p) => [p.id, p]));
        (0, vitest_1.expect)(byId['host-1'].isEliminated).toBe(true);
        (0, vitest_1.expect)(byId['p2'].isEliminated).toBe(false);
        (0, vitest_1.expect)(byId['p3'].isEliminated).toBe(true);
    });
});
