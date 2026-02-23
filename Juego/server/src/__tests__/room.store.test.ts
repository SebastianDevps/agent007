import { describe, it, expect, beforeEach } from 'vitest'
import {
  createRoom,
  getRoom,
  deleteRoom,
  addPlayer,
  removePlayer,
  serializePlayers,
  findRoomByPlayerId,
} from '../rooms/room.store'
import type { Player, Room } from '../rooms/room.types'

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

function makePlayer(id: string, name: string, overrides?: Partial<Player>): Player {
  return {
    id,
    name,
    role: null,
    isAlive: true,
    sessionToken: '',
    ...overrides,
  }
}

/**
 * The room store uses a module-level Map that persists between tests.
 * We clear it before each test by deleting every room that was created.
 * We track created codes via a local array to avoid coupling to internals.
 */
let createdCodes: string[] = []

beforeEach(() => {
  for (const code of createdCodes) {
    deleteRoom(code)
  }
  createdCodes = []
})

function trackRoom(room: Room): Room {
  createdCodes.push(room.code)
  return room
}

// ---------------------------------------------------------------------------
// createRoom
// ---------------------------------------------------------------------------

describe('createRoom', () => {
  it('creates a room with a 6-character uppercase code', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))

    expect(room.code).toHaveLength(6)
    expect(room.code).toBe(room.code.toUpperCase())
  })

  it('creates rooms with unique codes across multiple calls', () => {
    const codes = new Set<string>()
    for (let i = 0; i < 20; i++) {
      const room = trackRoom(createRoom(`host-${i}`, `Host ${i}`))
      codes.add(room.code)
    }
    // All 20 rooms should have distinct codes
    expect(codes.size).toBe(20)
  })

  it('sets the correct hostId', () => {
    const room = trackRoom(createRoom('host-42', 'Bob'))
    expect(room.hostId).toBe('host-42')
  })

  it('creates room in lobby phase', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    expect(room.phase).toBe('lobby')
  })

  it('adds the host as the sole initial player', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    expect(room.players.size).toBe(1)
    expect(room.players.has('host-1')).toBe(true)
  })

  it('host player has correct name and default values', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    const host = room.players.get('host-1')!

    expect(host.name).toBe('Alice')
    expect(host.role).toBeNull()
    expect(host.isAlive).toBe(true)
  })

  it('initializes config as null', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    expect(room.config).toBeNull()
  })

  it('stores the room so it can be retrieved with getRoom', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    const retrieved = getRoom(room.code)
    expect(retrieved).toBe(room)
  })
})

// ---------------------------------------------------------------------------
// addPlayer
// ---------------------------------------------------------------------------

describe('addPlayer', () => {
  it('adds a player to an existing room', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    const player = makePlayer('player-2', 'Bob')

    const success = addPlayer(room.code, player)

    expect(success).toBe(true)
    expect(room.players.has('player-2')).toBe(true)
    expect(room.players.get('player-2')!.name).toBe('Bob')
  })

  it('returns false for a non-existent room code', () => {
    const player = makePlayer('p1', 'Stranger')
    const result = addPlayer('NOROOM', player)
    expect(result).toBe(false)
  })

  it('returns false when the room already has 10 players (MAX_PLAYERS)', () => {
    const room = trackRoom(createRoom('host-1', 'Host'))
    // Fill to 10 (host is player 1, add 9 more)
    for (let i = 2; i <= 10; i++) {
      addPlayer(room.code, makePlayer(`p${i}`, `Player ${i}`))
    }
    expect(room.players.size).toBe(10)

    const eleventh = makePlayer('p11', 'One Too Many')
    const result = addPlayer(room.code, eleventh)

    expect(result).toBe(false)
    expect(room.players.size).toBe(10)
  })

  it('accepts the 10th player exactly (boundary)', () => {
    const room = trackRoom(createRoom('host-1', 'Host'))
    for (let i = 2; i <= 9; i++) {
      addPlayer(room.code, makePlayer(`p${i}`, `Player ${i}`))
    }
    expect(room.players.size).toBe(9)

    const tenth = makePlayer('p10', 'Player 10')
    const result = addPlayer(room.code, tenth)

    expect(result).toBe(true)
    expect(room.players.size).toBe(10)
  })

  it('preserves all player fields after adding', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    const player = makePlayer('p2', 'Carlos', { role: 'civil', isAlive: false })

    addPlayer(room.code, player)
    const stored = room.players.get('p2')!

    expect(stored.id).toBe('p2')
    expect(stored.name).toBe('Carlos')
    expect(stored.role).toBe('civil')
    expect(stored.isAlive).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// removePlayer
// ---------------------------------------------------------------------------

describe('removePlayer', () => {
  it('removes an existing player from the room', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    addPlayer(room.code, makePlayer('p2', 'Bob'))

    removePlayer(room.code, 'p2')

    expect(room.players.has('p2')).toBe(false)
    expect(room.players.size).toBe(1)
  })

  it('does nothing when the player does not exist in the room', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))

    expect(() => removePlayer(room.code, 'ghost-player')).not.toThrow()
    expect(room.players.size).toBe(1)
  })

  it('does nothing when the room code does not exist', () => {
    expect(() => removePlayer('NOROOM', 'p1')).not.toThrow()
  })

  it('can remove the host player', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))

    removePlayer(room.code, 'host-1')

    expect(room.players.has('host-1')).toBe(false)
    expect(room.players.size).toBe(0)
  })
})

// ---------------------------------------------------------------------------
// deleteRoom
// ---------------------------------------------------------------------------

describe('deleteRoom', () => {
  it('deletes a room so getRoom returns undefined', () => {
    const room = createRoom('host-1', 'Alice')
    const code = room.code

    deleteRoom(code)

    expect(getRoom(code)).toBeUndefined()
  })

  it('does nothing when the room code does not exist', () => {
    expect(() => deleteRoom('GHOST1')).not.toThrow()
  })

  it('only deletes the targeted room, leaving others intact', () => {
    const room1 = trackRoom(createRoom('host-1', 'Alice'))
    const room2 = trackRoom(createRoom('host-2', 'Bob'))

    deleteRoom(room1.code)
    // Remove room1 from tracking since we already deleted it
    createdCodes = createdCodes.filter((c) => c !== room1.code)

    expect(getRoom(room1.code)).toBeUndefined()
    expect(getRoom(room2.code)).toBeDefined()
  })
})

// ---------------------------------------------------------------------------
// findRoomByPlayerId
// ---------------------------------------------------------------------------

describe('findRoomByPlayerId', () => {
  it('returns the room containing the given player', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    addPlayer(room.code, makePlayer('p2', 'Bob'))

    const found = findRoomByPlayerId('p2')

    expect(found).toBeDefined()
    expect(found!.code).toBe(room.code)
  })

  it('finds the host player in their room', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))

    const found = findRoomByPlayerId('host-1')

    expect(found).toBeDefined()
    expect(found!.code).toBe(room.code)
  })

  it('returns undefined when the player is in no room', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    // Ensure the player is not in any room
    void room

    const found = findRoomByPlayerId('completely-unknown-player')
    expect(found).toBeUndefined()
  })

  it('returns the correct room when multiple rooms exist', () => {
    const room1 = trackRoom(createRoom('host-1', 'Alice'))
    const room2 = trackRoom(createRoom('host-2', 'Bob'))
    addPlayer(room2.code, makePlayer('p3', 'Carol'))

    const found = findRoomByPlayerId('p3')

    expect(found!.code).toBe(room2.code)
    expect(found!.code).not.toBe(room1.code)
  })

  it('returns undefined after the player is removed from the room', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    addPlayer(room.code, makePlayer('p2', 'Bob'))
    removePlayer(room.code, 'p2')

    const found = findRoomByPlayerId('p2')
    expect(found).toBeUndefined()
  })
})

// ---------------------------------------------------------------------------
// serializePlayers
// ---------------------------------------------------------------------------

describe('serializePlayers', () => {
  it('returns an array with one entry per player', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    addPlayer(room.code, makePlayer('p2', 'Bob'))

    const serialized = serializePlayers(room)

    expect(serialized).toHaveLength(2)
  })

  it('marks isHost=true only for the host', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    addPlayer(room.code, makePlayer('p2', 'Bob'))

    const serialized = serializePlayers(room)
    const hostEntry = serialized.find((p) => p.id === 'host-1')!
    const otherEntry = serialized.find((p) => p.id === 'p2')!

    expect(hostEntry.isHost).toBe(true)
    expect(otherEntry.isHost).toBe(false)
  })

  it('marks isHost=false for all non-host players', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    for (let i = 2; i <= 5; i++) {
      addPlayer(room.code, makePlayer(`p${i}`, `Player ${i}`))
    }

    const serialized = serializePlayers(room)
    const nonHosts = serialized.filter((p) => p.id !== 'host-1')

    for (const entry of nonHosts) {
      expect(entry.isHost).toBe(false)
    }
  })

  it('marks isEliminated=true for players in eliminatedIds', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    addPlayer(room.code, makePlayer('p2', 'Bob'))
    room.eliminatedIds.add('p2')

    const serialized = serializePlayers(room)
    const p2 = serialized.find((p) => p.id === 'p2')!

    expect(p2.isEliminated).toBe(true)
  })

  it('marks isEliminated=false for players not in eliminatedIds', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    addPlayer(room.code, makePlayer('p2', 'Bob'))

    const serialized = serializePlayers(room)
    const p2 = serialized.find((p) => p.id === 'p2')!

    expect(p2.isEliminated).toBe(false)
  })

  it('includes correct isAlive value for each player', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    addPlayer(room.code, makePlayer('p2', 'Bob', { isAlive: false }))

    const serialized = serializePlayers(room)
    const p2 = serialized.find((p) => p.id === 'p2')!

    expect(p2.isAlive).toBe(false)
  })

  it('includes correct name for each serialized player', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    addPlayer(room.code, makePlayer('p2', 'Bob'))

    const serialized = serializePlayers(room)
    const names = serialized.map((p) => p.name).sort()

    expect(names).toEqual(['Alice', 'Bob'])
  })

  it('does not expose role in serialized output', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    const player = makePlayer('p2', 'Bob', { role: 'impostor' })
    addPlayer(room.code, player)

    const serialized = serializePlayers(room)
    for (const entry of serialized) {
      expect(entry).not.toHaveProperty('role')
    }
  })

  it('returns empty array when room has no players', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    room.players.clear()

    const serialized = serializePlayers(room)
    expect(serialized).toEqual([])
  })

  it('correctly marks multiple eliminated players', () => {
    const room = trackRoom(createRoom('host-1', 'Alice'))
    addPlayer(room.code, makePlayer('p2', 'Bob'))
    addPlayer(room.code, makePlayer('p3', 'Carol'))
    room.eliminatedIds.add('host-1')
    room.eliminatedIds.add('p3')

    const serialized = serializePlayers(room)
    const byId = Object.fromEntries(serialized.map((p) => [p.id, p]))

    expect(byId['host-1'].isEliminated).toBe(true)
    expect(byId['p2'].isEliminated).toBe(false)
    expect(byId['p3'].isEliminated).toBe(true)
  })
})
