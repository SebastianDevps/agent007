"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerClueHandlers = registerClueHandlers;
const room_store_1 = require("../rooms/room.store");
const game_engine_1 = require("../game/game.engine");
function registerClueHandlers(socket, io) {
    /**
     * Submit a clue during the clue phase.
     * Only the current turn player can submit.
     * Once all alive players have submitted, move to voting.
     */
    socket.on('submit-clue', (clue) => {
        const room = findSocketRoom(socket);
        if (!room)
            return;
        if (room.phase !== 'clue-phase' && room.phase !== 'reveal') {
            console.warn(`[clue] ${socket.id} tried to submit clue in phase ${room.phase}`);
            return;
        }
        // If still in reveal, transition to clue-phase
        if (room.phase === 'reveal') {
            (0, room_store_1.updatePhase)(room.code, 'clue-phase');
        }
        // Validate it is this player's turn
        const currentPlayerId = room.turnOrder[room.currentTurnIndex];
        if (currentPlayerId !== socket.id) {
            console.warn(`[clue] ${socket.id} tried to submit clue but it's ${currentPlayerId}'s turn`);
            return;
        }
        // Store the clue
        room.clues.set(socket.id, clue);
        // Broadcast clue to room
        const player = room.players.get(socket.id);
        io.to(room.code).emit('clue-submitted', {
            playerId: socket.id,
            playerName: player?.name ?? '',
            clue,
        });
        console.log(`[clue] ${player?.name} submitted clue in room ${room.code}: "${clue}"`);
        // Check if all alive players have submitted clues
        const alivePlayers = Array.from(room.players.values()).filter((p) => p.isAlive && !room.eliminatedIds.has(p.id));
        const allSubmitted = alivePlayers.every((p) => room.clues.has(p.id));
        if (allSubmitted) {
            // Move to voting phase
            (0, room_store_1.updatePhase)(room.code, 'voting');
            io.to(room.code).emit('voting-started');
            console.log(`[clue] all clues submitted, voting started in room ${room.code}`);
        }
        else {
            // Advance to next turn
            room.currentTurnIndex = (0, game_engine_1.getNextTurnIndex)(room);
            const nextPlayerId = room.turnOrder[room.currentTurnIndex];
            const nextPlayer = room.players.get(nextPlayerId);
            io.to(room.code).emit('turn-started', {
                playerId: nextPlayerId,
                direction: room.turnDirection,
                round: room.currentRound,
            });
        }
    });
}
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
