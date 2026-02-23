import type { Server, Socket } from 'socket.io'
import { getRoom, updatePhase, serializePlayers } from '../rooms/room.store'
import { resolveVotes, checkVictory, getNextTurnIndex } from '../game/game.engine'
import type { Winner, Role } from '../rooms/room.types'

interface GameOverPayload {
  winner: Winner
  roles: Record<string, Role>
  word: string
}

function getGameOverPayload(
  room: ReturnType<typeof getRoom> & object
): GameOverPayload {
  return {
    winner: checkVictory(room) ?? 'impostores',
    roles: Object.fromEntries(
      Array.from(room.players.entries()).map(([id, p]) => [id, p.role ?? 'civil'])
    ),
    word: room.word ?? '',
  }
}

export function registerVoteHandlers(socket: Socket, io: Server): void {
  /**
   * Submit a vote during the voting phase.
   * Each alive player votes for who they think is the impostor.
   * Once all alive players have voted, resolve the round.
   */
  socket.on('submit-vote', (targetId: string) => {
    const room = findSocketRoom(socket)
    if (!room) return

    if (room.phase !== 'voting') {
      console.warn(
        `[vote] ${socket.id} tried to vote in phase ${room.phase}`
      )
      return
    }

    // Validate voter is alive
    const voter = room.players.get(socket.id)
    if (!voter || !voter.isAlive) {
      console.warn(`[vote] dead player ${socket.id} tried to vote`)
      return
    }

    // Rechazar doble voto: cada jugador solo puede votar una vez
    if (room.votes.has(socket.id)) {
      console.warn(`[vote] ${socket.id} already voted, ignoring duplicate`)
      return
    }

    // Validate target exists and is alive
    const target = room.players.get(targetId)
    if (!target || !target.isAlive) {
      console.warn(`[vote] ${socket.id} tried to vote for invalid target ${targetId}`)
      return
    }

    // No permitir votarse a sí mismo
    if (targetId === socket.id) {
      console.warn(`[vote] ${socket.id} tried to vote for self`)
      return
    }

    // Store vote
    room.votes.set(socket.id, targetId)

    // Broadcast that this player has voted (without revealing who)
    io.to(room.code).emit('vote-cast', socket.id)

    console.log(
      `[vote] ${voter.name} voted for ${target.name} in room ${room.code}`
    )

    // Check if all alive players have voted
    const alivePlayers = Array.from(room.players.values()).filter(
      (p) => p.isAlive && !room.eliminatedIds.has(p.id)
    )
    const allVoted = alivePlayers.every((p) => room.votes.has(p.id))

    if (!allVoted) return

    // Resolve votes
    const result = resolveVotes(room)

    // Emit round result to all players
    updatePhase(room.code, 'round-end')
    io.to(room.code).emit('round-result', {
      ...result,
      round: room.currentRound,
      players: serializePlayers(room),
    })

    console.log(
      `[vote] round ${room.currentRound} resolved in room ${room.code}`,
      result.eliminatedName
        ? `— eliminated: ${result.eliminatedName} (${result.eliminatedRole})`
        : '— tie, nobody eliminated'
    )

    // Check for immediate winner (impostor eliminated)
    if (result.winner) {
      updatePhase(room.code, 'game-over')
      const payload = getGameOverPayload(room)
      payload.winner = result.winner
      io.to(room.code).emit('game-over', payload)
      console.log(`[vote] game over in room ${room.code}: ${result.winner} win`)
      return
    }

    // Check general victory condition
    const winner = checkVictory(room)
    if (winner) {
      updatePhase(room.code, 'game-over')
      const payload = getGameOverPayload(room)
      payload.winner = winner
      io.to(room.code).emit('game-over', payload)
      console.log(`[vote] game over in room ${room.code}: ${winner} win`)
      return
    }

    // Check if more rounds remain
    const config = room.config
    if (config && room.currentRound >= config.rounds) {
      // All rounds done, impostors win
      updatePhase(room.code, 'game-over')
      const payload = getGameOverPayload(room)
      payload.winner = 'impostores'
      io.to(room.code).emit('game-over', payload)
      console.log(`[vote] game over in room ${room.code}: impostores win (all rounds done)`)
      return
    }

    // Start next round
    room.currentRound++
    room.clues.clear()
    room.votes.clear()
    updatePhase(room.code, 'clue-phase')

    // Set up next turn (first alive player in order)
    room.currentTurnIndex = 0
    // Find first alive player
    for (let i = 0; i < room.turnOrder.length; i++) {
      const pid = room.turnOrder[i]
      const p = room.players.get(pid)
      if (p && p.isAlive && !room.eliminatedIds.has(pid)) {
        room.currentTurnIndex = i
        break
      }
    }

    const nextPlayerId = room.turnOrder[room.currentTurnIndex]
    const nextPlayer = room.players.get(nextPlayerId)

    io.to(room.code).emit('turn-started', {
      playerId: nextPlayerId,
      direction: room.turnDirection,
      round: room.currentRound,
    })

    console.log(
      `[vote] round ${room.currentRound} started in room ${room.code}`
    )
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
