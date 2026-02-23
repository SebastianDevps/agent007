import { nanoid } from 'nanoid'
import type { Room, Player, GamePhase } from './room.types'

const MAX_PLAYERS = 10
const ROOM_EMPTY_GRACE_MS = 15_000

const rooms = new Map<string, Room>()
const pendingDeletes = new Map<string, NodeJS.Timeout>()

/** Índice: sessionToken → { roomCode, socketId actual } */
const tokenIndex = new Map<string, { roomCode: string; socketId: string }>()

export function indexToken(token: string, roomCode: string, socketId: string): void {
  tokenIndex.set(token, { roomCode, socketId })
}

export function lookupToken(token: string): { roomCode: string; socketId: string } | undefined {
  return tokenIndex.get(token)
}

export function removeToken(token: string): void {
  tokenIndex.delete(token)
}

/**
 * Reemplaza el socket.id viejo por el nuevo en toda la estructura de la sala:
 * players map, turnOrder, clues, votes, eliminatedIds y hostId.
 */
export function replacePlayerSocket(code: string, oldId: string, newId: string): Player | undefined {
  const room = rooms.get(code)
  if (!room) return undefined

  const player = room.players.get(oldId)
  if (!player) return undefined

  player.id = newId
  room.players.delete(oldId)
  room.players.set(newId, player)

  if (room.hostId === oldId) room.hostId = newId

  room.turnOrder = room.turnOrder.map(id => id === oldId ? newId : id)

  if (room.clues.has(oldId)) {
    const clue = room.clues.get(oldId)!
    room.clues.delete(oldId)
    room.clues.set(newId, clue)
  }

  if (room.votes.has(oldId)) {
    const vote = room.votes.get(oldId)!
    room.votes.delete(oldId)
    room.votes.set(newId, vote)
  }
  for (const [voterId, targetId] of room.votes.entries()) {
    if (targetId === oldId) room.votes.set(voterId, newId)
  }

  if (room.eliminatedIds.has(oldId)) {
    room.eliminatedIds.delete(oldId)
    room.eliminatedIds.add(newId)
  }

  if (room.readyPlayers.has(oldId)) {
    room.readyPlayers.delete(oldId)
    room.readyPlayers.add(newId)
  }

  return player
}

function generateCode(): string {
  return nanoid(6).toUpperCase()
}

export function createRoom(hostId: string, hostName: string, sessionToken: string = ''): Room {
  const code = generateCode()

  const host: Player = {
    id: hostId,
    name: hostName,
    role: null,
    isAlive: true,
    sessionToken,
  }

  const room: Room = {
    code,
    hostId,
    phase: 'lobby',
    players: new Map([[hostId, host]]),
    config: null,
    word: null,
    referenceWord: null,
    hint: null,
    currentRound: 1,
    turnOrder: [],
    currentTurnIndex: 0,
    turnDirection: 'right',
    clues: new Map(),
    votes: new Map(),
    eliminatedIds: new Set(),
    readyPlayers: new Set(),
    readyTimeout: null,
  }

  rooms.set(code, room)
  return room
}

export function getRoom(code: string): Room | undefined {
  return rooms.get(code)
}

export function deleteRoom(code: string): void {
  cancelScheduledDeletion(code)
  rooms.delete(code)
}

/** Programar borrado de la sala tras un periodo de gracia (reconexión). */
export function scheduleRoomDeletion(code: string): void {
  cancelScheduledDeletion(code)
  const timeout = setTimeout(() => {
    pendingDeletes.delete(code)
    rooms.delete(code)
    console.log(`[connection] room ${code} deleted (empty after grace period)`)
  }, ROOM_EMPTY_GRACE_MS)
  pendingDeletes.set(code, timeout)
}

export function cancelScheduledDeletion(code: string): void {
  const timeout = pendingDeletes.get(code)
  if (timeout) {
    clearTimeout(timeout)
    pendingDeletes.delete(code)
  }
}

export function addPlayer(code: string, player: Player): boolean {
  const room = rooms.get(code)
  if (!room) return false
  if (room.players.size >= MAX_PLAYERS) return false

  room.players.set(player.id, player)
  cancelScheduledDeletion(code)
  return true
}

export function removePlayer(code: string, playerId: string): void {
  const room = rooms.get(code)
  if (!room) return

  room.players.delete(playerId)
}

export function updatePhase(code: string, phase: GamePhase): void {
  const room = rooms.get(code)
  if (!room) return

  room.phase = phase
}

/** Serialize players Map to a plain array for emitting over Socket.IO */
export function serializePlayers(room: Room): Array<{
  id: string
  name: string
  isHost: boolean
  isAlive: boolean
  isEliminated: boolean
}> {
  return Array.from(room.players.values()).map((p) => ({
    id: p.id,
    name: p.name,
    isHost: p.id === room.hostId,
    isAlive: p.isAlive,
    isEliminated: room.eliminatedIds.has(p.id),
  }))
}

/** Find which room a player belongs to */
export function findRoomByPlayerId(playerId: string): Room | undefined {
  for (const room of rooms.values()) {
    if (room.players.has(playerId)) {
      return room
    }
  }
  return undefined
}
