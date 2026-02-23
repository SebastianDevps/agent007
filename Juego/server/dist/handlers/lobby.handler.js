"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerLobbyHandlers = registerLobbyHandlers;
const nanoid_1 = require("nanoid");
const room_store_1 = require("../rooms/room.store");
const word_service_1 = require("../words/word.service");
const game_engine_1 = require("../game/game.engine");
function registerLobbyHandlers(socket, io) {
    /**
     * Create a new room.
     * Client sends the host player name.
     * Callback receives the room code.
     */
    socket.on('create-room', (name, cb) => {
        try {
            const existingRoom = (0, room_store_1.findRoomByPlayerId)(socket.id);
            if (existingRoom) {
                (0, room_store_1.removePlayer)(existingRoom.code, socket.id);
                socket.leave(existingRoom.code);
                if (existingRoom.players.size === 0) {
                    (0, room_store_1.scheduleRoomDeletion)(existingRoom.code);
                }
            }
            const token = (0, nanoid_1.nanoid)(16);
            const room = (0, room_store_1.createRoom)(socket.id, name, token);
            (0, room_store_1.indexToken)(token, room.code, socket.id);
            void socket.join(room.code);
            const players = (0, room_store_1.serializePlayers)(room);
            io.to(room.code).emit('room-updated', players);
            console.log(`[lobby] room ${room.code} created by ${name} (${socket.id})`);
            cb(room.code, players, token);
        }
        catch (err) {
            console.error('[lobby] create-room error:', err);
            cb('');
        }
    });
    /**
     * Join an existing room.
     * Client sends { code, name, sessionToken? }.
     * Callback receives (error?, sessionToken?) — token is the stable reconnection key.
     */
    socket.on('join-room', (data, cb) => {
        const code = data.code.toUpperCase();
        const room = (0, room_store_1.getRoom)(code);
        if (!room) {
            cb('ROOM_NOT_FOUND');
            return;
        }
        // ── Path de RECONEXIÓN: el cliente envía un token previo ──
        if (data.sessionToken) {
            const lookup = (0, room_store_1.lookupToken)(data.sessionToken);
            if (lookup && lookup.roomCode === code) {
                const oldId = lookup.socketId;
                if (oldId === socket.id) {
                    // Misma conexión (ej. Strict Mode doble mount), idempotente
                    void socket.join(code);
                    io.to(code).emit('room-updated', (0, room_store_1.serializePlayers)(room));
                    cb(undefined, data.sessionToken);
                    if (room.config)
                        socket.emit('config-updated', room.config);
                    resendGameState(socket, io, room, socket.id);
                    return;
                }
                // Swap oldId → socket.id en toda la sala
                const player = (0, room_store_1.replacePlayerSocket)(code, oldId, socket.id);
                if (player) {
                    (0, room_store_1.indexToken)(data.sessionToken, code, socket.id);
                    void socket.join(code);
                    io.to(code).emit('room-updated', (0, room_store_1.serializePlayers)(room));
                    console.log(`[lobby] ${data.name} reconectó a ${code} (${oldId} → ${socket.id})`);
                    cb(undefined, data.sessionToken);
                    if (room.config)
                        socket.emit('config-updated', room.config);
                    resendGameState(socket, io, room, socket.id);
                    return;
                }
                // Si el token es válido pero el player ya no existe, caer al path normal
            }
        }
        // ── Path NORMAL: nuevo jugador ──
        if (room.phase !== 'lobby') {
            cb('GAME_STARTED');
            return;
        }
        const alreadyInRoom = room.players.has(socket.id);
        const token = (0, nanoid_1.nanoid)(16);
        const player = {
            id: socket.id,
            name: data.name,
            role: null,
            isAlive: true,
            sessionToken: token,
        };
        if (alreadyInRoom) {
            // Idempotente: ya estaba (doble clic / Strict Mode). Actualizar nombre y reenviar lista.
            room.players.set(socket.id, player);
            void socket.join(code);
            io.to(code).emit('room-updated', (0, room_store_1.serializePlayers)(room));
            cb(undefined, token);
            if (room.config)
                socket.emit('config-updated', room.config);
            return;
        }
        const added = (0, room_store_1.addPlayer)(code, player);
        if (!added) {
            cb('ROOM_FULL');
            return;
        }
        // Si la sala estaba vacía (periodo de gracia), el que entra es el nuevo host
        if (room.players.size === 1) {
            room.hostId = socket.id;
        }
        (0, room_store_1.indexToken)(token, code, socket.id);
        void socket.join(code);
        io.to(code).emit('room-updated', (0, room_store_1.serializePlayers)(room));
        console.log(`[lobby] ${data.name} (${socket.id}) se unió a ${code}`);
        cb(undefined, token);
        if (room.config)
            socket.emit('config-updated', room.config);
    });
    /**
     * Update game configuration. Only the host can do this.
     */
    socket.on('update-config', (config) => {
        // Find the room this socket belongs to
        const room = findSocketRoom(socket);
        if (!room)
            return;
        if (room.hostId !== socket.id) {
            console.warn(`[lobby] non-host ${socket.id} tried to update config`);
            return;
        }
        room.config = config;
        io.to(room.code).emit('config-updated', config);
        console.log(`[lobby] config updated for room ${room.code}`);
    });
    /**
     * Start the game. Only the host can do this.
     * Requires at least 2 players and a valid config.
     */
    socket.on('start-game', async (cb) => {
        const room = findSocketRoom(socket);
        if (!room) {
            cb?.('ROOM_NOT_FOUND');
            return;
        }
        if (room.hostId !== socket.id) {
            cb?.('NOT_HOST');
            return;
        }
        if (room.players.size < 2) {
            cb?.('NOT_ENOUGH_PLAYERS');
            return;
        }
        if (!room.config) {
            cb?.('NO_CONFIG');
            return;
        }
        try {
            // Fetch word pair from Supabase
            const wordPair = await (0, word_service_1.getRandomWordPair)(room.config.categoryId);
            room.word = wordPair.word;
            room.referenceWord = wordPair.ref;
            // Assign roles and set up turn order
            (0, game_engine_1.assignRoles)(room);
            (0, room_store_1.updatePhase)(room.code, 'reveal');
            // Notify all players that game has started
            io.to(room.code).emit('game-started');
            // Send each player their individual role and word.
            // El impostor recibe null: sólo conoce la categoría, no la palabra exacta.
            for (const [playerId, player] of room.players.entries()) {
                const wordForPlayer = player.role === 'impostor' ? null : room.word;
                io.to(playerId).emit('role-assigned', {
                    role: player.role,
                    word: wordForPlayer,
                });
            }
            // No emitir turn-started aquí. Esperar a que todos confirmen
            // su rol con 'player-ready'. Si alguno no confirma en 15s,
            // el timeout de emitFirstTurn lo dispara automáticamente.
            room.readyPlayers = new Set();
            room.readyTimeout = setTimeout(() => {
                room.readyTimeout = null;
                emitFirstTurn(io, room);
            }, 15_000);
            console.log(`[lobby] game started in room ${room.code} — word: ${room.word}, ref: ${room.referenceWord}`);
            cb?.();
        }
        catch (error) {
            const message = error instanceof Error ? error.message : 'Unknown error starting game';
            console.error(`[lobby] start-game error:`, message);
            cb?.('START_ERROR');
        }
    });
    /**
     * Emitido por el cliente al voltear su role card.
     * Cuando todos los jugadores vivos confirman, se dispara el primer turno.
     */
    socket.on('player-ready', () => {
        const room = findSocketRoom(socket);
        if (!room || room.phase !== 'reveal')
            return;
        room.readyPlayers.add(socket.id);
        console.log(`[lobby] player-ready: ${socket.id} en ${room.code} (${room.readyPlayers.size}/${room.players.size})`);
        const alivePlayers = Array.from(room.players.values()).filter(p => p.isAlive);
        if (room.readyPlayers.size >= alivePlayers.length) {
            emitFirstTurn(io, room);
        }
    });
}
/**
 * Lanza el primer turno de la partida.
 * Cancela el timeout si todavía está activo.
 * Idempotente: no hace nada si la sala ya salió de 'reveal'.
 */
function emitFirstTurn(io, room) {
    if (room.phase !== 'reveal')
        return;
    if (room.readyTimeout) {
        clearTimeout(room.readyTimeout);
        room.readyTimeout = null;
    }
    (0, room_store_1.updatePhase)(room.code, 'clue-phase');
    const firstPlayerId = room.turnOrder[room.currentTurnIndex];
    io.to(room.code).emit('turn-started', {
        playerId: firstPlayerId,
        direction: room.turnDirection,
        round: room.currentRound,
    });
    console.log(`[lobby] primer turno disparado en sala ${room.code} → ${firstPlayerId}`);
}
/**
 * Find the room a socket belongs to by checking its joined rooms.
 * Socket.IO rooms include the socket's own ID, so we filter that out.
 */
function findSocketRoom(socket) {
    const { getRoom } = require('../rooms/room.store');
    for (const roomCode of socket.rooms) {
        if (roomCode === socket.id)
            continue;
        const room = getRoom(roomCode);
        if (room)
            return room;
    }
    return undefined;
}
/**
 * Re-envía el estado del juego a un jugador que acaba de reconectar mid-game.
 * Esto le permite saber en qué fase está y recuperar su rol y turno.
 */
function resendGameState(socket, io, room, playerId) {
    if (room.phase === 'lobby')
        return;
    socket.emit('game-started');
    const player = room.players.get(playerId);
    if (player?.role) {
        const wordForPlayer = player.role === 'impostor' ? null : room.word;
        socket.emit('role-assigned', {
            role: player.role,
            word: wordForPlayer,
        });
    }
    // En 'reveal' no re-enviamos turn-started: el jugador debe volver
    // a voltear su card y emitir player-ready para sincronizarse.
    if (room.phase === 'clue-phase') {
        socket.emit('turn-started', {
            playerId: room.turnOrder[room.currentTurnIndex],
            direction: room.turnDirection,
            round: room.currentRound,
        });
        // Re-enviar pistas ya emitidas en esta ronda
        if (room.clues.size > 0) {
            const history = Array.from(room.clues.entries()).map(([pid, clue]) => ({
                playerId: pid,
                playerName: room.players.get(pid)?.name ?? 'Jugador',
                clue,
            }));
            socket.emit('clues-history', history);
        }
    }
    if (room.phase === 'voting') {
        socket.emit('voting-started');
    }
}
