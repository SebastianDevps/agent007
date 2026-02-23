"use strict";
/**
 * game.e2e.test.ts
 *
 * Integration E2E tests for "El Impostor" Socket.IO server.
 * Spins up a real HTTP + Socket.IO server on a random port and connects
 * real socket.io-client instances to exercise the full event pipeline.
 *
 * Run: vitest run src/__tests__/game.e2e.test.ts
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const http_1 = require("http");
const socket_io_1 = require("socket.io");
const socket_io_client_1 = require("socket.io-client");
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const vitest_1 = require("vitest");
// ---------------------------------------------------------------------------
// Mock word.service so start-game never touches Supabase
// ---------------------------------------------------------------------------
vitest_1.vi.mock('../words/word.service', () => ({
    getActiveCategories: vitest_1.vi.fn().mockResolvedValue([
        { id: 'cat-1', name: 'Test', emoji: '🧪' },
    ]),
    getRandomWordPair: vitest_1.vi.fn().mockResolvedValue({ word: 'perro', ref: 'lobo' }),
}));
// ---------------------------------------------------------------------------
// Handlers (imported AFTER the mock above is in place)
// ---------------------------------------------------------------------------
const lobby_handler_1 = require("../handlers/lobby.handler");
const clue_handler_1 = require("../handlers/clue.handler");
const vote_handler_1 = require("../handlers/vote.handler");
const connection_handler_1 = require("../handlers/connection.handler");
function buildTestServer() {
    return new Promise((resolve, reject) => {
        const app = (0, express_1.default)();
        app.use((0, cors_1.default)());
        app.use(express_1.default.json());
        const httpServer = (0, http_1.createServer)(app);
        const io = new socket_io_1.Server(httpServer, {
            cors: { origin: '*', methods: ['GET', 'POST'] },
            // Reduce polling overhead in tests
            transports: ['websocket'],
        });
        io.on('connection', (socket) => {
            (0, lobby_handler_1.registerLobbyHandlers)(socket, io);
            (0, clue_handler_1.registerClueHandlers)(socket, io);
            (0, vote_handler_1.registerVoteHandlers)(socket, io);
            (0, connection_handler_1.registerConnectionHandlers)(socket, io);
        });
        httpServer.listen(0, () => {
            const addr = httpServer.address();
            if (!addr || typeof addr === 'string') {
                reject(new Error('Could not determine server address'));
                return;
            }
            const url = `http://localhost:${addr.port}`;
            resolve({
                io,
                url,
                close: () => new Promise((res) => {
                    // io.close() closes all sockets AND the underlying HTTP server.
                    // Calling httpServer.close() again after would throw ERR_SERVER_NOT_RUNNING.
                    io.close(() => res());
                }),
            });
        });
    });
}
function makeClient(url) {
    return (0, socket_io_client_1.io)(url, {
        transports: ['websocket'],
        autoConnect: false,
    });
}
function connect(socket) {
    return new Promise((resolve, reject) => {
        socket.once('connect', resolve);
        socket.once('connect_error', reject);
        socket.connect();
    });
}
function waitFor(socket, event) {
    return new Promise((resolve) => socket.once(event, resolve));
}
function disconnectAll(...sockets) {
    return Promise.all(sockets.map((s) => new Promise((resolve) => {
        if (!s.connected) {
            resolve();
            return;
        }
        s.once('disconnect', () => resolve());
        s.disconnect();
    })));
}
// ---------------------------------------------------------------------------
// Global server shared across all suites
// ---------------------------------------------------------------------------
let server;
(0, vitest_1.beforeAll)(async () => {
    server = await buildTestServer();
});
(0, vitest_1.afterAll)(async () => {
    await server.close();
});
// ===========================================================================
// Suite: Lobby flow
// ===========================================================================
(0, vitest_1.describe)('Lobby flow', () => {
    let host;
    let guest;
    (0, vitest_1.beforeEach)(async () => {
        host = makeClient(server.url);
        guest = makeClient(server.url);
        await connect(host);
    });
    (0, vitest_1.afterEach)(async () => {
        await disconnectAll(host, guest);
    });
    (0, vitest_1.it)('crear sala y recibir code', async () => {
        const code = await new Promise((resolve) => {
            host.emit('create-room', 'Alice', (code) => resolve(code));
        });
        (0, vitest_1.expect)(typeof code).toBe('string');
        (0, vitest_1.expect)(code).toHaveLength(6);
        // nanoid uses URL-safe alphabet — all uppercase after toUpperCase()
        (0, vitest_1.expect)(code).toMatch(/^[A-Z0-9_-]{6}$/);
    });
    (0, vitest_1.it)('unirse a sala existente — ambos reciben room-updated con 2 jugadores', async () => {
        await connect(guest);
        const code = await new Promise((resolve) => {
            host.emit('create-room', 'Alice', resolve);
        });
        // After host creates room, both clients should ultimately see 2 players.
        // We listen for room-updated on host BEFORE guest joins.
        const roomUpdatedPromise = waitFor(host, 'room-updated');
        const err = await new Promise((resolve) => {
            guest.emit('join-room', { code, name: 'Bob' }, resolve);
        });
        (0, vitest_1.expect)(err).toBeUndefined();
        // Host receives room-updated with 2 players
        const players = await roomUpdatedPromise;
        (0, vitest_1.expect)(players).toHaveLength(2);
        const names = players.map((p) => p.name);
        (0, vitest_1.expect)(names).toContain('Alice');
        (0, vitest_1.expect)(names).toContain('Bob');
        (0, vitest_1.expect)(players.find((p) => p.name === 'Alice')?.isHost).toBe(true);
    });
    (0, vitest_1.it)('error al unirse a sala inexistente — callback con ROOM_NOT_FOUND', async () => {
        await connect(guest);
        const err = await new Promise((resolve) => {
            guest.emit('join-room', { code: 'XXXXXX', name: 'Charlie' }, resolve);
        });
        (0, vitest_1.expect)(err).toBe('ROOM_NOT_FOUND');
    });
    (0, vitest_1.it)('error al unirse a partida en curso — callback con GAME_STARTED', async () => {
        await connect(guest);
        // Create room and start game manually by manipulating state via a second
        // client that also joins, then we trigger start-game. We need at least 2
        // players, so we use a third socket.
        const third = makeClient(server.url);
        await connect(third);
        const code = await new Promise((resolve) => {
            host.emit('create-room', 'Alice', resolve);
        });
        await new Promise((resolve) => {
            third.emit('join-room', { code, name: 'Dave' }, () => resolve());
        });
        // Set config then start game
        host.emit('update-config', {
            impostorCount: 1,
            rounds: 1,
            categoryId: 'cat-1',
            categoryName: 'Test',
        });
        await new Promise((resolve) => {
            host.emit('start-game', resolve);
        });
        // Now guest tries to join the in-progress room
        const err = await new Promise((resolve) => {
            guest.emit('join-room', { code, name: 'Lateomer' }, resolve);
        });
        (0, vitest_1.expect)(err).toBe('GAME_STARTED');
        await disconnectAll(third);
    });
    (0, vitest_1.it)('solo el host puede actualizar config — non-host no emite config-updated', async () => {
        await connect(guest);
        const code = await new Promise((resolve) => {
            host.emit('create-room', 'Alice', resolve);
        });
        await new Promise((resolve) => {
            guest.emit('join-room', { code, name: 'Bob' }, () => resolve());
        });
        // Listen for config-updated — should NOT arrive
        let configReceived = false;
        host.on('config-updated', () => {
            configReceived = true;
        });
        guest.on('config-updated', () => {
            configReceived = true;
        });
        guest.emit('update-config', {
            impostorCount: 1,
            rounds: 1,
            categoryId: 'cat-1',
            categoryName: 'Test',
        });
        // Wait a short time to ensure no event arrives
        await new Promise((r) => setTimeout(r, 150));
        (0, vitest_1.expect)(configReceived).toBe(false);
    });
    (0, vitest_1.it)('config-updated llega a todos — host actualiza, todos reciben el evento', async () => {
        await connect(guest);
        const code = await new Promise((resolve) => {
            host.emit('create-room', 'Alice', resolve);
        });
        await new Promise((resolve) => {
            guest.emit('join-room', { code, name: 'Bob' }, () => resolve());
        });
        const config = {
            impostorCount: 1,
            rounds: 2,
            categoryId: 'cat-1',
            categoryName: 'Test',
        };
        const [hostConfig, guestConfig] = await Promise.all([
            waitFor(host, 'config-updated'),
            waitFor(guest, 'config-updated'),
            // Emit after listeners are registered
            new Promise((r) => {
                setTimeout(() => {
                    host.emit('update-config', config);
                    r();
                }, 10);
            }),
        ]);
        (0, vitest_1.expect)(hostConfig).toEqual(config);
        (0, vitest_1.expect)(guestConfig).toEqual(config);
    });
});
// ===========================================================================
// Suite: Game flow (2 jugadores)
// ===========================================================================
(0, vitest_1.describe)('Game flow (2 jugadores)', () => {
    let host;
    let guest;
    let roomCode;
    (0, vitest_1.beforeEach)(async () => {
        host = makeClient(server.url);
        guest = makeClient(server.url);
        await connect(host);
        await connect(guest);
        roomCode = await new Promise((resolve) => {
            host.emit('create-room', 'Alice', resolve);
        });
        await new Promise((resolve) => {
            guest.emit('join-room', { code: roomCode, name: 'Bob' }, () => resolve());
        });
    });
    (0, vitest_1.afterEach)(async () => {
        await disconnectAll(host, guest);
    });
    (0, vitest_1.it)('flujo completo de partida', async () => {
        // ------------------------------------------------------------------
        // 1. update-config
        // ------------------------------------------------------------------
        const config = {
            impostorCount: 1,
            rounds: 1,
            categoryId: 'cat-1',
            categoryName: 'Test',
        };
        host.emit('update-config', config);
        await new Promise((r) => setTimeout(r, 30));
        // ------------------------------------------------------------------
        // 2. start-game → game-started + role-assigned (×2) + turn-started
        // ------------------------------------------------------------------
        const hostGameStarted = waitFor(host, 'game-started');
        const guestGameStarted = waitFor(guest, 'game-started');
        const hostRole = waitFor(host, 'role-assigned');
        const guestRole = waitFor(guest, 'role-assigned');
        const firstTurn = waitFor(host, 'turn-started');
        const startError = await new Promise((resolve) => {
            host.emit('start-game', resolve);
        });
        (0, vitest_1.expect)(startError).toBeUndefined();
        await Promise.all([hostGameStarted, guestGameStarted]);
        const [hr, gr] = await Promise.all([hostRole, guestRole]);
        (0, vitest_1.expect)(['civil', 'impostor']).toContain(hr.role);
        (0, vitest_1.expect)(['civil', 'impostor']).toContain(gr.role);
        // Exactly one impostor in a 2-player game with impostorCount=1
        const roles = [hr.role, gr.role];
        (0, vitest_1.expect)(roles.filter((r) => r === 'impostor')).toHaveLength(1);
        // civil gets real word, impostor gets reference word
        (0, vitest_1.expect)(typeof hr.word).toBe('string');
        (0, vitest_1.expect)(hr.word.length).toBeGreaterThan(0);
        const turn = await firstTurn;
        (0, vitest_1.expect)(turn).toMatchObject({
            direction: vitest_1.expect.stringMatching(/^(left|right)$/),
            round: 1,
        });
        (0, vitest_1.expect)(typeof turn.playerId).toBe('string');
        // ------------------------------------------------------------------
        // 3. clue phase — figure out who goes first
        // ------------------------------------------------------------------
        const firstPlayerId = turn.playerId;
        // Map socket.id → ClientSocket
        const socketById = {
            [host.id]: host,
            [guest.id]: guest,
        };
        const firstSocket = socketById[firstPlayerId];
        const secondSocket = firstSocket === host ? guest : host;
        // First player submits clue → clue-submitted + turn-started (not voting yet)
        const clue1Received = waitFor(host, 'clue-submitted');
        firstSocket.emit('submit-clue', 'mi pista uno');
        const clue1 = await clue1Received;
        (0, vitest_1.expect)(clue1.clue).toBe('mi pista uno');
        (0, vitest_1.expect)(clue1.playerId).toBe(firstPlayerId);
        // Second player submits clue → clue-submitted + voting-started
        const clue2Received = waitFor(host, 'clue-submitted');
        const votingStartedHost = waitFor(host, 'voting-started');
        const votingStartedGuest = waitFor(guest, 'voting-started');
        secondSocket.emit('submit-clue', 'mi pista dos');
        await Promise.all([clue2Received, votingStartedHost, votingStartedGuest]);
        // ------------------------------------------------------------------
        // 4. voting phase — both vote, first one votes for second and vice-versa
        // ------------------------------------------------------------------
        // vote-cast is broadcast to ALL players in the room, so each socket
        // receives N events (one per voter). We collect all N from a single
        // socket instead of using .once on each socket independently.
        const collectVoteCasts = (n) => new Promise((resolve) => {
            const ids = [];
            const handler = (voterId) => {
                ids.push(voterId);
                if (ids.length >= n) {
                    host.off('vote-cast', handler);
                    resolve(ids);
                }
            };
            host.on('vote-cast', handler);
        });
        const voteCastCollector = collectVoteCasts(2);
        const roundResultHost = waitFor(host, 'round-result');
        const roundResultGuest = waitFor(guest, 'round-result');
        // Collect game-over or turn-started (whichever arrives)
        let gameOverPayload = null;
        const gameOverOrNextTurn = new Promise((resolve) => {
            host.once('game-over', (payload) => {
                gameOverPayload = payload;
                resolve();
            });
            host.once('turn-started', () => resolve());
        });
        host.emit('submit-vote', guest.id);
        guest.emit('submit-vote', host.id);
        const castIds = await voteCastCollector;
        // vote-cast emits the voterId — should be host.id and guest.id in some order
        (0, vitest_1.expect)(castIds).toEqual(vitest_1.expect.arrayContaining([host.id, guest.id]));
        const [resHost, resGuest] = await Promise.all([roundResultHost, roundResultGuest]);
        (0, vitest_1.expect)(resHost.round).toBe(1);
        (0, vitest_1.expect)(resGuest.round).toBe(1);
        // With 2 players voting for each other it's a tie → no elimination,
        // but with 1 round config the game ends immediately after.
        await gameOverOrNextTurn;
        // If game-over arrived, verify shape
        if (gameOverPayload !== null) {
            const payload = gameOverPayload;
            (0, vitest_1.expect)(['civiles', 'impostores']).toContain(payload.winner);
            (0, vitest_1.expect)(typeof payload.word).toBe('string');
            (0, vitest_1.expect)(typeof payload.roles).toBe('object');
        }
    });
});
// ===========================================================================
// Suite: Edge cases
// ===========================================================================
(0, vitest_1.describe)('Edge cases', () => {
    let host;
    let guest;
    (0, vitest_1.beforeEach)(async () => {
        host = makeClient(server.url);
        guest = makeClient(server.url);
        await connect(host);
        await connect(guest);
    });
    (0, vitest_1.afterEach)(async () => {
        await disconnectAll(host, guest);
    });
    (0, vitest_1.it)('desconexión del host transfiere host al siguiente jugador', async () => {
        const code = await new Promise((resolve) => {
            host.emit('create-room', 'Alice', resolve);
        });
        await new Promise((resolve) => {
            guest.emit('join-room', { code, name: 'Bob' }, () => resolve());
        });
        // Listen for room-updated on guest after host disconnects
        const roomUpdatedAfterDisconnect = waitFor(guest, 'room-updated');
        host.disconnect();
        const players = await roomUpdatedAfterDisconnect;
        // Only Bob remains
        (0, vitest_1.expect)(players).toHaveLength(1);
        (0, vitest_1.expect)(players[0].name).toBe('Bob');
        (0, vitest_1.expect)(players[0].isHost).toBe(true);
    });
    (0, vitest_1.it)('desconexión de jugador en sala vacía elimina la sala', async () => {
        // Single player creates room then disconnects
        const solo = makeClient(server.url);
        await connect(solo);
        const code = await new Promise((resolve) => {
            solo.emit('create-room', 'Solo', resolve);
        });
        // Disconnect the only player
        await new Promise((resolve) => {
            solo.once('disconnect', resolve);
            solo.disconnect();
        });
        // Give the server a tick to process the disconnect
        await new Promise((r) => setTimeout(r, 100));
        // A new client tries to join that room — should get ROOM_NOT_FOUND
        const newClient = makeClient(server.url);
        await connect(newClient);
        const err = await new Promise((resolve) => {
            newClient.emit('join-room', { code, name: 'Latecomer' }, resolve);
        });
        (0, vitest_1.expect)(err).toBe('ROOM_NOT_FOUND');
        await disconnectAll(newClient);
    });
});
