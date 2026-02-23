import { nanoid } from 'nanoid'
import type { Server, Socket } from 'socket.io'
import {
  createRoom,
  getRoom,
  addPlayer,
  removePlayer,
  updatePhase,
  serializePlayers,
  findRoomByPlayerId,
  scheduleRoomDeletion,
  indexToken,
  lookupToken,
  replacePlayerSocket,
} from '../rooms/room.store'
import { getRandomWordPair } from '../words/word.service'
import { assignRoles, checkVictory } from '../game/game.engine'
import type { Player, GameConfig, Room } from '../rooms/room.types'

export function registerLobbyHandlers(socket: Socket, io: Server): void {
  /**
   * Create a new room.
   * Client sends the host player name.
   * Callback receives the room code.
   */
  socket.on('create-room', (name: string, cb: (code: string, players?: ReturnType<typeof serializePlayers>, sessionToken?: string) => void) => {
    try {
      const existingRoom = findRoomByPlayerId(socket.id)
      if (existingRoom) {
        removePlayer(existingRoom.code, socket.id)
        socket.leave(existingRoom.code)
        if (existingRoom.players.size === 0) {
          scheduleRoomDeletion(existingRoom.code)
        }
      }
      const token = nanoid(16)
      const room = createRoom(socket.id, name, token)
      indexToken(token, room.code, socket.id)
      void socket.join(room.code)
      const players = serializePlayers(room)
      io.to(room.code).emit('room-updated', players)
      console.log(`[lobby] room ${room.code} created by ${name} (${socket.id})`)
      cb(room.code, players, token)
    } catch (err) {
      console.error('[lobby] create-room error:', err)
      cb('')
    }
  })

  /**
   * Join an existing room.
   * Client sends { code, name, sessionToken? }.
   * Callback receives (error?, sessionToken?) — token is the stable reconnection key.
   */
  socket.on(
    'join-room',
    (data: { code: string; name: string; sessionToken?: string }, cb: (error?: string, sessionToken?: string) => void) => {
      const code = data.code.toUpperCase()
      const room = getRoom(code)

      if (!room) {
        cb('ROOM_NOT_FOUND')
        return
      }

      // ── Path de RECONEXIÓN: el cliente envía un token previo ──
      if (data.sessionToken) {
        const lookup = lookupToken(data.sessionToken)
        if (lookup && lookup.roomCode === code) {
          const oldId = lookup.socketId

          if (oldId === socket.id) {
            // Misma conexión (ej. Strict Mode doble mount), idempotente
            void socket.join(code)
            io.to(code).emit('room-updated', serializePlayers(room))
            cb(undefined, data.sessionToken)
            if (room.config) socket.emit('config-updated', room.config)
            resendGameState(socket, io, room, socket.id)
            return
          }

          // Swap oldId → socket.id en toda la sala
          const player = replacePlayerSocket(code, oldId, socket.id)
          if (player) {
            indexToken(data.sessionToken, code, socket.id)
            void socket.join(code)
            io.to(code).emit('room-updated', serializePlayers(room))
            console.log(`[lobby] ${data.name} reconectó a ${code} (${oldId} → ${socket.id})`)
            cb(undefined, data.sessionToken)
            if (room.config) socket.emit('config-updated', room.config)
            resendGameState(socket, io, room, socket.id)
            return
          }
          // Si el token es válido pero el player ya no existe, caer al path normal
        }
      }

      // ── Path NORMAL: nuevo jugador ──
      if (room.phase !== 'lobby') {
        cb('GAME_STARTED')
        return
      }

      const alreadyInRoom = room.players.has(socket.id)
      const token = nanoid(16)
      const player: Player = {
        id: socket.id,
        name: data.name,
        role: null,
        isAlive: true,
        sessionToken: token,
      }

      if (alreadyInRoom) {
        // Idempotente: ya estaba (doble clic / Strict Mode). Actualizar nombre y reenviar lista.
        room.players.set(socket.id, player)
        void socket.join(code)
        io.to(code).emit('room-updated', serializePlayers(room))
        cb(undefined, token)
        if (room.config) socket.emit('config-updated', room.config)
        return
      }

      const added = addPlayer(code, player)
      if (!added) {
        cb('ROOM_FULL')
        return
      }

      // Si la sala estaba vacía (periodo de gracia), el que entra es el nuevo host
      if (room.players.size === 1) {
        room.hostId = socket.id
      }

      indexToken(token, code, socket.id)
      void socket.join(code)
      io.to(code).emit('room-updated', serializePlayers(room))
      console.log(`[lobby] ${data.name} (${socket.id}) se unió a ${code}`)
      cb(undefined, token)
      if (room.config) socket.emit('config-updated', room.config)
    }
  )

  /**
   * Update game configuration. Only the host can do this.
   */
  socket.on('update-config', (config: GameConfig) => {
    // Find the room this socket belongs to
    const room = findSocketRoom(socket)
    if (!room) return

    if (room.hostId !== socket.id) {
      console.warn(`[lobby] non-host ${socket.id} tried to update config`)
      return
    }

    room.config = config
    io.to(room.code).emit('config-updated', config)
    console.log(`[lobby] config updated for room ${room.code}`)
  })

  /**
   * Start the game. Only the host can do this.
   * Requires at least 2 players and a valid config.
   */
  socket.on('start-game', async (cb?: (error?: string) => void) => {
    const room = findSocketRoom(socket)
    if (!room) {
      cb?.('ROOM_NOT_FOUND')
      return
    }

    if (room.hostId !== socket.id) {
      cb?.('NOT_HOST')
      return
    }

    if (room.players.size < 2) {
      cb?.('NOT_ENOUGH_PLAYERS')
      return
    }

    if (!room.config) {
      cb?.('NO_CONFIG')
      return
    }

    try {
      // Fetch word pair from Supabase
      const wordPair = await getRandomWordPair(room.config.categoryId)
      room.word = wordPair.word
      room.referenceWord = wordPair.ref
      room.hint = wordPair.hint ?? null

      // Assign roles and set up turn order
      assignRoles(room)
      updatePhase(room.code, 'reveal')

      // Notify all players that game has started
      io.to(room.code).emit('game-started')

      // Send each player their individual role and word.
      // El impostor recibe null: sólo conoce la categoría, no la palabra exacta.
      for (const [playerId, player] of room.players.entries()) {
        if (player.role === 'impostor') {
          const hint = room.config.difficulty === 'easy' ? (room.hint ?? null) : null
          io.to(playerId).emit('role-assigned', {
            role: 'impostor',
            word: null,
            hint,
          })
        } else {
          io.to(playerId).emit('role-assigned', {
            role: player.role,
            word: room.word,
          })
        }
      }

      // No emitir turn-started aquí. Esperar a que todos confirmen
      // su rol con 'player-ready'. Si alguno no confirma en 15s,
      // el timeout de emitFirstTurn lo dispara automáticamente.
      room.readyPlayers = new Set()
      room.readyTimeout = setTimeout(() => {
        room.readyTimeout = null
        emitFirstTurn(io, room)
      }, 15_000)

      console.log(
        `[lobby] game started in room ${room.code} — word: ${room.word}, ref: ${room.referenceWord}`
      )
      cb?.()
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Unknown error starting game'
      console.error(`[lobby] start-game error:`, message)
      cb?.('START_ERROR')
    }
  })

  /**
   * Reiniciar la partida en la misma sala con los mismos jugadores.
   * Solo el host puede hacerlo. Obtiene nueva palabra de la misma categoría.
   */
  socket.on('restart-game', async (cb?: (error?: string) => void) => {
    const room = findSocketRoom(socket)
    if (!room) { cb?.('ROOM_NOT_FOUND'); return }
    if (room.hostId !== socket.id) { cb?.('NOT_HOST'); return }
    if (!room.config) { cb?.('NO_CONFIG'); return }

    try {
      const wordPair = await getRandomWordPair(room.config.categoryId)
      room.word = wordPair.word
      room.referenceWord = wordPair.ref
      room.hint = wordPair.hint ?? null

      // Reset round state completely
      room.currentRound = 1
      room.clues = new Map()
      room.votes = new Map()
      room.eliminatedIds = new Set()
      room.readyPlayers = new Set()
      if (room.readyTimeout) {
        clearTimeout(room.readyTimeout)
        room.readyTimeout = null
      }

      // Re-assign roles (also resets isAlive for all players + shuffles turnOrder)
      assignRoles(room)
      updatePhase(room.code, 'reveal')

      // Notify all players
      io.to(room.code).emit('game-started')
      io.to(room.code).emit('room-updated', serializePlayers(room))

      for (const [playerId, player] of room.players.entries()) {
        if (player.role === 'impostor') {
          const hint = room.config.difficulty === 'easy' ? (room.hint ?? null) : null
          io.to(playerId).emit('role-assigned', { role: 'impostor', word: null, hint })
        } else {
          io.to(playerId).emit('role-assigned', { role: player.role, word: room.word })
        }
      }

      room.readyTimeout = setTimeout(() => {
        room.readyTimeout = null
        emitFirstTurn(io, room)
      }, 15_000)

      console.log(`[lobby] restart-game en sala ${room.code} — nueva palabra: ${room.word}`)
      cb?.()
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      console.error('[lobby] restart-game error:', message)
      cb?.('START_ERROR')
    }
  })

  /**
   * Solo el host puede iniciar la votación desde la pantalla de discusión.
   * Transiciona la sala a 'voting' y notifica a todos.
   */
  socket.on('start-vote', () => {
    const room = findSocketRoom(socket)
    if (!room) {
      console.warn(`[lobby] start-vote: no room found for socket ${socket.id}`)
      return
    }
    if (room.hostId !== socket.id) {
      console.warn(`[lobby] start-vote: non-host ${socket.id} tried to start vote`)
      return
    }
    if (room.phase !== 'clue-phase') {
      console.warn(`[lobby] start-vote: wrong phase '${room.phase}' for socket ${socket.id}`)
      return
    }

    room.votes.clear()
    updatePhase(room.code, 'voting')
    io.to(room.code).emit('voting-started')
    console.log(`[lobby] votación iniciada en sala ${room.code} por ${socket.id}`)
  })

  /**
   * Emitido por el cliente al voltear su role card.
   * Cuando todos los jugadores vivos confirman, se dispara el primer turno.
   */
  socket.on('player-ready', () => {
    const room = findSocketRoom(socket)
    if (!room || room.phase !== 'reveal') return

    room.readyPlayers.add(socket.id)
    console.log(
      `[lobby] player-ready: ${socket.id} en ${room.code} (${room.readyPlayers.size}/${room.players.size})`
    )

    const alivePlayers = Array.from(room.players.values()).filter(p => p.isAlive)
    if (room.readyPlayers.size >= alivePlayers.length) {
      emitFirstTurn(io, room)
    }
  })
}

/**
 * Lanza el primer turno de la partida.
 * Cancela el timeout si todavía está activo.
 * Idempotente: no hace nada si la sala ya salió de 'reveal'.
 */
function emitFirstTurn(io: Server, room: Room): void {
  if (room.phase !== 'reveal') return

  if (room.readyTimeout) {
    clearTimeout(room.readyTimeout)
    room.readyTimeout = null
  }

  updatePhase(room.code, 'clue-phase')

  const firstPlayerId = room.turnOrder[room.currentTurnIndex]
  io.to(room.code).emit('turn-started', {
    playerId: firstPlayerId,
    direction: room.turnDirection,
    round: room.currentRound,
  })

  console.log(`[lobby] primer turno disparado en sala ${room.code} → ${firstPlayerId}`)
}

/**
 * Find the room a socket belongs to by checking its joined rooms.
 * Socket.IO rooms include the socket's own ID, so we filter that out.
 */
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

/**
 * Re-envía el estado del juego a un jugador que acaba de reconectar mid-game.
 * Esto le permite saber en qué fase está y recuperar su rol y turno.
 */
function resendGameState(socket: Socket, io: Server, room: Room, playerId: string): void {
  if (room.phase === 'lobby') return

  socket.emit('game-started')

  const player = room.players.get(playerId)
  if (player?.role) {
    if (player.role === 'impostor') {
      const hint = room.config?.difficulty === 'easy' ? (room.hint ?? null) : null
      socket.emit('role-assigned', { role: 'impostor', word: null, hint })
    } else {
      socket.emit('role-assigned', { role: player.role, word: room.word })
    }
  }

  if (room.phase === 'reveal') {
    // Verificar si ya hay quorum (todos los demás ya habían confirmado).
    // Con readyPlayers correctamente migrado, si este jugador ya estaba
    // en readyPlayers y los demás también, disparamos el turno ahora.
    const alivePlayers = Array.from(room.players.values()).filter(p => p.isAlive)
    if (room.readyPlayers.size >= alivePlayers.length) {
      emitFirstTurn(io, room)
    }
    // Si no hay quorum, el jugador verá su carta y deberá voltearla para emitir player-ready.
    return
  }

  if (room.phase === 'clue-phase') {
    socket.emit('turn-started', {
      playerId: room.turnOrder[room.currentTurnIndex],
      direction: room.turnDirection,
      round: room.currentRound,
    })

    // Re-enviar pistas ya emitidas en esta ronda
    if (room.clues.size > 0) {
      const history = Array.from(room.clues.entries()).map(([pid, clue]) => ({
        playerId: pid,
        playerName: room.players.get(pid)?.name ?? 'Jugador',
        clue,
      }))
      socket.emit('clues-history', history)
    }
    return
  }

  if (room.phase === 'voting') {
    socket.emit('voting-started')
    return
  }

  if (room.phase === 'game-over') {
    const winner = checkVictory(room) ?? 'impostores'
    const roles = Object.fromEntries(
      Array.from(room.players.entries()).map(([id, p]) => [id, p.role ?? 'civil'])
    )
    socket.emit('game-over', { winner, roles, word: room.word ?? '' })
  }
}
