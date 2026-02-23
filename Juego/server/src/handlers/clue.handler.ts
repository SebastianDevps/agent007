import type { Server, Socket } from 'socket.io'
import { getRoom, updatePhase } from '../rooms/room.store'
import { getNextTurnIndex } from '../game/game.engine'

export function registerClueHandlers(socket: Socket, io: Server): void {
  /**
   * Submit a clue during the clue phase.
   * Only the current turn player can submit.
   * Once all alive players have submitted, move to voting.
   */
  socket.on('submit-clue', (clue: string) => {
    const room = findSocketRoom(socket)
    if (!room) return

    if (room.phase !== 'clue-phase' && room.phase !== 'reveal') {
      console.warn(
        `[clue] ${socket.id} tried to submit clue in phase ${room.phase}`
      )
      return
    }

    // If still in reveal, transition to clue-phase
    if (room.phase === 'reveal') {
      updatePhase(room.code, 'clue-phase')
    }

    // Validate it is this player's turn
    const currentPlayerId = room.turnOrder[room.currentTurnIndex]
    if (currentPlayerId !== socket.id) {
      console.warn(
        `[clue] ${socket.id} tried to submit clue but it's ${currentPlayerId}'s turn`
      )
      return
    }

    // Store the clue
    room.clues.set(socket.id, clue)

    // Broadcast clue to room
    const player = room.players.get(socket.id)
    io.to(room.code).emit('clue-submitted', {
      playerId: socket.id,
      playerName: player?.name ?? '',
      clue,
    })

    console.log(
      `[clue] ${player?.name} submitted clue in room ${room.code}: "${clue}"`
    )

    // Check if all alive players have submitted clues
    const alivePlayers = Array.from(room.players.values()).filter(
      (p) => p.isAlive && !room.eliminatedIds.has(p.id)
    )
    const allSubmitted = alivePlayers.every((p) => room.clues.has(p.id))

    if (allSubmitted) {
      // Move to voting phase
      updatePhase(room.code, 'voting')
      io.to(room.code).emit('voting-started')
      console.log(`[clue] all clues submitted, voting started in room ${room.code}`)
    } else {
      // Advance to next turn
      room.currentTurnIndex = getNextTurnIndex(room)
      const nextPlayerId = room.turnOrder[room.currentTurnIndex]
      const nextPlayer = room.players.get(nextPlayerId)

      io.to(room.code).emit('turn-started', {
        playerId: nextPlayerId,
        direction: room.turnDirection,
        round: room.currentRound,
      })
    }
  })
}

function findSocketRoom(socket: Socket) {
  const { getRoom, findRoomByPlayerId } = require('../rooms/room.store') as typeof import('../rooms/room.store')
  for (const roomCode of socket.rooms) {
    if (roomCode === socket.id) continue
    const room = getRoom(roomCode)
    if (room) return room
  }
  // Fallback: find by player ID in case socket lost Socket.IO room membership
  const room = findRoomByPlayerId(socket.id)
  if (room) void socket.join(room.code)
  return room
}
