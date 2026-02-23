"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.indexToken = indexToken;
exports.lookupToken = lookupToken;
exports.removeToken = removeToken;
exports.replacePlayerSocket = replacePlayerSocket;
exports.createRoom = createRoom;
exports.getRoom = getRoom;
exports.deleteRoom = deleteRoom;
exports.scheduleRoomDeletion = scheduleRoomDeletion;
exports.cancelScheduledDeletion = cancelScheduledDeletion;
exports.addPlayer = addPlayer;
exports.removePlayer = removePlayer;
exports.updatePhase = updatePhase;
exports.serializePlayers = serializePlayers;
exports.findRoomByPlayerId = findRoomByPlayerId;
const nanoid_1 = require("nanoid");
const MAX_PLAYERS = 10;
const ROOM_EMPTY_GRACE_MS = 15_000;
const rooms = new Map();
const pendingDeletes = new Map();
/** Índice: sessionToken → { roomCode, socketId actual } */
const tokenIndex = new Map();
function indexToken(token, roomCode, socketId) {
    tokenIndex.set(token, { roomCode, socketId });
}
function lookupToken(token) {
    return tokenIndex.get(token);
}
function removeToken(token) {
    tokenIndex.delete(token);
}
/**
 * Reemplaza el socket.id viejo por el nuevo en toda la estructura de la sala:
 * players map, turnOrder, clues, votes, eliminatedIds y hostId.
 */
function replacePlayerSocket(code, oldId, newId) {
    const room = rooms.get(code);
    if (!room)
        return undefined;
    const player = room.players.get(oldId);
    if (!player)
        return undefined;
    player.id = newId;
    room.players.delete(oldId);
    room.players.set(newId, player);
    if (room.hostId === oldId)
        room.hostId = newId;
    room.turnOrder = room.turnOrder.map(id => id === oldId ? newId : id);
    if (room.clues.has(oldId)) {
        const clue = room.clues.get(oldId);
        room.clues.delete(oldId);
        room.clues.set(newId, clue);
    }
    if (room.votes.has(oldId)) {
        const vote = room.votes.get(oldId);
        room.votes.delete(oldId);
        room.votes.set(newId, vote);
    }
    for (const [voterId, targetId] of room.votes.entries()) {
        if (targetId === oldId)
            room.votes.set(voterId, newId);
    }
    if (room.eliminatedIds.has(oldId)) {
        room.eliminatedIds.delete(oldId);
        room.eliminatedIds.add(newId);
    }
    return player;
}
function generateCode() {
    return (0, nanoid_1.nanoid)(6).toUpperCase();
}
function createRoom(hostId, hostName, sessionToken = '') {
    const code = generateCode();
    const host = {
        id: hostId,
        name: hostName,
        role: null,
        isAlive: true,
        sessionToken,
    };
    const room = {
        code,
        hostId,
        phase: 'lobby',
        players: new Map([[hostId, host]]),
        config: null,
        word: null,
        referenceWord: null,
        currentRound: 1,
        turnOrder: [],
        currentTurnIndex: 0,
        turnDirection: 'right',
        clues: new Map(),
        votes: new Map(),
        eliminatedIds: new Set(),
        readyPlayers: new Set(),
        readyTimeout: null,
    };
    rooms.set(code, room);
    return room;
}
function getRoom(code) {
    return rooms.get(code);
}
function deleteRoom(code) {
    cancelScheduledDeletion(code);
    rooms.delete(code);
}
/** Programar borrado de la sala tras un periodo de gracia (reconexión). */
function scheduleRoomDeletion(code) {
    cancelScheduledDeletion(code);
    const timeout = setTimeout(() => {
        pendingDeletes.delete(code);
        rooms.delete(code);
        console.log(`[connection] room ${code} deleted (empty after grace period)`);
    }, ROOM_EMPTY_GRACE_MS);
    pendingDeletes.set(code, timeout);
}
function cancelScheduledDeletion(code) {
    const timeout = pendingDeletes.get(code);
    if (timeout) {
        clearTimeout(timeout);
        pendingDeletes.delete(code);
    }
}
function addPlayer(code, player) {
    const room = rooms.get(code);
    if (!room)
        return false;
    if (room.players.size >= MAX_PLAYERS)
        return false;
    room.players.set(player.id, player);
    cancelScheduledDeletion(code);
    return true;
}
function removePlayer(code, playerId) {
    const room = rooms.get(code);
    if (!room)
        return;
    room.players.delete(playerId);
}
function updatePhase(code, phase) {
    const room = rooms.get(code);
    if (!room)
        return;
    room.phase = phase;
}
/** Serialize players Map to a plain array for emitting over Socket.IO */
function serializePlayers(room) {
    return Array.from(room.players.values()).map((p) => ({
        id: p.id,
        name: p.name,
        isHost: p.id === room.hostId,
        isAlive: p.isAlive,
        isEliminated: room.eliminatedIds.has(p.id),
    }));
}
/** Find which room a player belongs to */
function findRoomByPlayerId(playerId) {
    for (const room of rooms.values()) {
        if (room.players.has(playerId)) {
            return room;
        }
    }
    return undefined;
}
