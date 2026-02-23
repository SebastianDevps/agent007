"use strict";
/**
 * stress.test.ts
 *
 * Stress / load tests for "El Impostor" Socket.IO server.
 * Measures throughput, concurrency, and latency under load.
 *
 * Run: vitest run --reporter=verbose src/__tests__/stress.test.ts
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
// Mock word.service — identical to E2E suite so Supabase is never called
// ---------------------------------------------------------------------------
vitest_1.vi.mock('../words/word.service', () => ({
    getActiveCategories: vitest_1.vi.fn().mockResolvedValue([
        { id: 'cat-1', name: 'Test', emoji: '🧪' },
    ]),
    getRandomWordPair: vitest_1.vi.fn().mockResolvedValue({ word: 'perro', ref: 'lobo' }),
}));
const lobby_handler_1 = require("../handlers/lobby.handler");
const clue_handler_1 = require("../handlers/clue.handler");
const vote_handler_1 = require("../handlers/vote.handler");
const connection_handler_1 = require("../handlers/connection.handler");
function buildTestServer() {
    return new Promise((resolve, reject) => {
        const app = (0, express_1.default)();
        app.use((0, cors_1.default)());
        const httpServer = (0, http_1.createServer)(app);
        const io = new socket_io_1.Server(httpServer, {
            cors: { origin: '*', methods: ['GET', 'POST'] },
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
                reject(new Error('Could not determine address'));
                return;
            }
            const url = `http://localhost:${addr.port}`;
            resolve({
                io,
                url,
                close: () => new Promise((res) => {
                    // io.close() closes all sockets AND the underlying HTTP server.
                    io.close(() => res());
                }),
            });
        });
    });
}
function makeClient(url) {
    return (0, socket_io_client_1.io)(url, { transports: ['websocket'], autoConnect: false });
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
// Global server — one instance for all stress tests to share
// ---------------------------------------------------------------------------
let server;
(0, vitest_1.beforeAll)(async () => {
    server = await buildTestServer();
}, 15_000);
(0, vitest_1.afterAll)(async () => {
    await server.close();
});
// ===========================================================================
// Stress Suite
// ===========================================================================
(0, vitest_1.describe)('Stress tests', () => {
    // -------------------------------------------------------------------------
    // 1. 10 salas concurrentes
    // -------------------------------------------------------------------------
    (0, vitest_1.it)('10 salas concurrentes — todas con código único', async () => {
        const N = 10;
        const clients = await Promise.all(Array.from({ length: N }, async () => {
            const s = makeClient(server.url);
            await connect(s);
            return s;
        }));
        const t0 = Date.now();
        const codes = await Promise.all(clients.map((s) => new Promise((resolve) => {
            s.emit('create-room', `Host-${s.id?.slice(0, 4)}`, (code) => resolve(code));
        })));
        const elapsed = Date.now() - t0;
        console.log(`[stress] 10 salas concurrentes creadas en ${elapsed}ms`);
        // All codes must be unique
        const unique = new Set(codes);
        (0, vitest_1.expect)(unique.size).toBe(N);
        // All codes have 6 characters
        codes.forEach((c) => (0, vitest_1.expect)(c).toHaveLength(6));
        await disconnectAll(...clients);
    }, 10_000);
    // -------------------------------------------------------------------------
    // 2. Sala con 10 jugadores — el 11º es rechazado con ROOM_FULL
    // -------------------------------------------------------------------------
    (0, vitest_1.it)('sala con 10 jugadores — el jugador 11 recibe ROOM_FULL', async () => {
        const MAX = 10;
        // Create host and room
        const hostSocket = makeClient(server.url);
        await connect(hostSocket);
        const code = await new Promise((resolve) => {
            hostSocket.emit('create-room', 'RoomHost', (c) => resolve(c));
        });
        // Join 9 more players (host is already #1)
        const guests = await Promise.all(Array.from({ length: MAX - 1 }, async (_, i) => {
            const s = makeClient(server.url);
            await connect(s);
            return s;
        }));
        const t0 = Date.now();
        await Promise.all(guests.map((s, i) => new Promise((resolve) => {
            s.emit('join-room', { code, name: `Player-${i + 2}` }, () => resolve());
        })));
        const elapsed = Date.now() - t0;
        console.log(`[stress] 10 jugadores unidos en ${elapsed}ms`);
        // 11th player should be rejected
        const overflow = makeClient(server.url);
        await connect(overflow);
        const err = await new Promise((resolve) => {
            overflow.emit('join-room', { code, name: 'Overflow' }, resolve);
        });
        (0, vitest_1.expect)(err).toBe('ROOM_FULL');
        await disconnectAll(hostSocket, overflow, ...guests);
    }, 10_000);
    // -------------------------------------------------------------------------
    // 3. 100 creaciones de sala en secuencia — tiempo total < 2000ms
    // -------------------------------------------------------------------------
    (0, vitest_1.it)('100 creaciones de sala en secuencia — tiempo < 2000ms', async () => {
        const client = makeClient(server.url);
        await connect(client);
        const t0 = Date.now();
        for (let i = 0; i < 100; i++) {
            await new Promise((resolve) => {
                client.emit('create-room', `SeqHost-${i}`, (code) => resolve(code));
            });
        }
        const elapsed = Date.now() - t0;
        console.log(`[stress] 100 creaciones secuenciales en ${elapsed}ms`);
        (0, vitest_1.expect)(elapsed).toBeLessThan(2_000);
        await disconnectAll(client);
    }, 10_000);
    // -------------------------------------------------------------------------
    // 4. Broadcast a 8 jugadores simultáneos — config-updated en < 500ms
    // -------------------------------------------------------------------------
    (0, vitest_1.it)('broadcast a 8 jugadores — config-updated llega a todos en < 500ms', async () => {
        const PLAYERS = 8;
        const hostSocket = makeClient(server.url);
        await connect(hostSocket);
        const code = await new Promise((resolve) => {
            hostSocket.emit('create-room', 'BroadcastHost', (c) => resolve(c));
        });
        // Connect 7 guests
        const guests = await Promise.all(Array.from({ length: PLAYERS - 1 }, async (_, i) => {
            const s = makeClient(server.url);
            await connect(s);
            return s;
        }));
        await Promise.all(guests.map((s, i) => new Promise((resolve) => {
            s.emit('join-room', { code, name: `BPlayer-${i + 2}` }, () => resolve());
        })));
        const config = {
            impostorCount: 1,
            rounds: 2,
            categoryId: 'cat-1',
            categoryName: 'Stress Test',
        };
        // Arm listeners on all clients BEFORE emitting
        const allReceived = Promise.all([
            waitFor(hostSocket, 'config-updated'),
            ...guests.map((s) => waitFor(s, 'config-updated')),
        ]);
        const t0 = Date.now();
        hostSocket.emit('update-config', config);
        await allReceived;
        const elapsed = Date.now() - t0;
        console.log(`[stress] config-updated recibido por ${PLAYERS} jugadores en ${elapsed}ms`);
        (0, vitest_1.expect)(elapsed).toBeLessThan(500);
        await disconnectAll(hostSocket, ...guests);
    }, 10_000);
    // -------------------------------------------------------------------------
    // 5. Partida rápida con 4 jugadores — lobby → juego → votos → resultado
    // -------------------------------------------------------------------------
    (0, vitest_1.it)('partida rápida con 4 jugadores — flujo completo medido', async () => {
        const N_PLAYERS = 4;
        const hostSocket = makeClient(server.url);
        await connect(hostSocket);
        const code = await new Promise((resolve) => {
            hostSocket.emit('create-room', 'FastHost', (c) => resolve(c));
        });
        const guests = await Promise.all(Array.from({ length: N_PLAYERS - 1 }, async (_, i) => {
            const s = makeClient(server.url);
            await connect(s);
            return s;
        }));
        await Promise.all(guests.map((s, i) => new Promise((resolve) => {
            s.emit('join-room', { code, name: `FPlayer-${i + 2}` }, () => resolve());
        })));
        const allSockets = [hostSocket, ...guests];
        const t0 = Date.now();
        // --- Config ---
        const config = {
            impostorCount: 1,
            rounds: 1,
            categoryId: 'cat-1',
            categoryName: 'Stress Test',
        };
        hostSocket.emit('update-config', config);
        await new Promise((r) => setTimeout(r, 20));
        // --- start-game ---
        const gameStartedAll = Promise.all(allSockets.map((s) => waitFor(s, 'game-started')));
        const rolesAll = Promise.all(allSockets.map((s) => waitFor(s, 'role-assigned')));
        const firstTurn = waitFor(hostSocket, 'turn-started');
        await new Promise((resolve) => {
            hostSocket.emit('start-game', resolve);
        });
        await gameStartedAll;
        const roles = await rolesAll;
        (0, vitest_1.expect)(roles.every((r) => ['civil', 'impostor'].includes(r.role))).toBe(true);
        const impostorCount = roles.filter((r) => r.role === 'impostor').length;
        (0, vitest_1.expect)(impostorCount).toBe(1);
        const turn = await firstTurn;
        // --- Clue phase: each player submits in turn order ---
        // We need to drive turns in order. We'll do it by listening for turn-started.
        const socketById = {};
        allSockets.forEach((s) => {
            if (s.id)
                socketById[s.id] = s;
        });
        // Collect all clue submissions until voting-started
        const votingStarted = waitFor(hostSocket, 'voting-started');
        let pendingTurnPlayerId = turn.playerId;
        // Submit clues one by one following turn-started events
        const submitCluesInOrder = async () => {
            const remaining = new Set(allSockets.map((s) => s.id));
            while (remaining.size > 0) {
                const currentSocket = socketById[pendingTurnPlayerId];
                if (!currentSocket)
                    break;
                remaining.delete(pendingTurnPlayerId);
                // Listen for the next turn-started BEFORE emitting (to avoid race)
                const nextTurnPromise = remaining.size > 0
                    ? waitFor(hostSocket, 'turn-started')
                    : Promise.resolve({ playerId: '' });
                currentSocket.emit('submit-clue', `clue-from-${pendingTurnPlayerId.slice(0, 4)}`);
                if (remaining.size > 0) {
                    const next = await nextTurnPromise;
                    pendingTurnPlayerId = next.playerId;
                }
            }
        };
        await submitCluesInOrder();
        await votingStarted;
        // --- Voting phase ---
        // Each player votes for the next player in allSockets (circular)
        const allVoteCasts = new Promise((resolve) => {
            let received = 0;
            hostSocket.on('vote-cast', () => {
                received++;
                if (received >= N_PLAYERS)
                    resolve();
            });
        });
        const roundResult = waitFor(hostSocket, 'round-result');
        // Set up game-over or next-turn listener
        const gameOrNext = new Promise((resolve) => {
            hostSocket.once('game-over', () => resolve());
            hostSocket.once('turn-started', () => resolve());
        });
        // Each player votes for the "next" socket (non-self target)
        allSockets.forEach((s, i) => {
            const target = allSockets[(i + 1) % N_PLAYERS];
            s.emit('submit-vote', target.id);
        });
        await allVoteCasts;
        await roundResult;
        await gameOrNext;
        const elapsed = Date.now() - t0;
        console.log(`[stress] partida rápida 4 jugadores completada en ${elapsed}ms`);
        // Whole flow should complete in a reasonable time
        (0, vitest_1.expect)(elapsed).toBeLessThan(5_000);
        await disconnectAll(...allSockets);
    }, 10_000);
});
