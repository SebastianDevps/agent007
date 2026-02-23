"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerConnectionHandlers = registerConnectionHandlers;
const room_store_1 = require("../rooms/room.store");
function registerConnectionHandlers(socket, io) {
    socket.on('disconnect', () => {
        const room = (0, room_store_1.findRoomByPlayerId)(socket.id);
        if (!room)
            return;
        const wasHost = room.hostId === socket.id;
        const playerName = room.players.get(socket.id)?.name ?? 'unknown';
        if (room.phase === 'lobby') {
            // En lobby: remover normalmente
            (0, room_store_1.removePlayer)(room.code, socket.id);
            console.log(`[connection] ${playerName} (${socket.id}) salió del lobby ${room.code}`);
            if (room.players.size === 0) {
                (0, room_store_1.scheduleRoomDeletion)(room.code);
                console.log(`[connection] sala ${room.code} programada para borrado (vacía)`);
                return;
            }
            if (wasHost) {
                const newHost = Array.from(room.players.values()).find((p) => p.isAlive)
                    ?? Array.from(room.players.values())[0];
                if (newHost) {
                    room.hostId = newHost.id;
                    console.log(`[connection] nuevo host en ${room.code}: ${newHost.name}`);
                }
            }
            io.to(room.code).emit('room-updated', (0, room_store_1.serializePlayers)(room));
        }
        else {
            // Mid-game: mantener datos del jugador para reconexión por sessionToken
            console.log(`[connection] ${playerName} (${socket.id}) desconectado mid-game de ${room.code} (retenido para reconexión)`);
            io.to(room.code).emit('player-disconnected', socket.id);
        }
    });
}
