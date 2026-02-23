import { describe, it, expect, vi, beforeEach } from 'vitest'
import { assignRoles, getNextTurnIndex, resolveVotes, checkVictory } from '../game/game.engine'
import type { Room, Player } from '../rooms/room.types'

// ---------------------------------------------------------------------------
// Test helper
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

function makeRoom(overrides?: Partial<Room>): Room {
  return {
    code: 'TEST01',
    hostId: 'host-1',
    phase: 'lobby',
    players: new Map([['host-1', makePlayer('host-1', 'Host')]]),
    config: { impostorCount: 1, rounds: 3, categoryId: 'cat-1', categoryName: 'Test', difficulty: 'hard' },
    word: 'perro',
    referenceWord: 'lobo',
    hint: null,
    currentRound: 1,
    turnOrder: ['host-1'],
    currentTurnIndex: 0,
    turnDirection: 'right',
    clues: new Map(),
    votes: new Map(),
    eliminatedIds: new Set(),
    readyPlayers: new Set(),
    readyTimeout: null,
    ...overrides,
  }
}

/** Build a room with N players, all alive, roles unset. */
function makeRoomWithPlayers(count: number, impostorCount = 1, rounds = 3): Room {
  const players = new Map<string, Player>()
  for (let i = 1; i <= count; i++) {
    const id = `player-${i}`
    players.set(id, makePlayer(id, `Player ${i}`))
  }
  return makeRoom({
    hostId: 'player-1',
    players,
    config: { impostorCount, rounds, categoryId: 'cat-1', categoryName: 'Test', difficulty: 'hard' },
    turnOrder: Array.from(players.keys()),
  })
}

// ---------------------------------------------------------------------------
// assignRoles
// ---------------------------------------------------------------------------

describe('assignRoles', () => {
  beforeEach(() => {
    // Reset any Math.random mock after each test
    vi.restoreAllMocks()
  })

  it('assigns exactly N impostors according to config', () => {
    const room = makeRoomWithPlayers(6, 2)
    assignRoles(room)

    const impostors = Array.from(room.players.values()).filter((p) => p.role === 'impostor')
    expect(impostors).toHaveLength(2)
  })

  it('assigns civil role to all non-impostor players', () => {
    const room = makeRoomWithPlayers(6, 2)
    assignRoles(room)

    const civiles = Array.from(room.players.values()).filter((p) => p.role === 'civil')
    expect(civiles).toHaveLength(4)
  })

  it('assigns every player a role (no null roles after call)', () => {
    const room = makeRoomWithPlayers(5, 1)
    assignRoles(room)

    for (const player of room.players.values()) {
      expect(player.role).not.toBeNull()
    }
  })

  it('shuffles turnOrder and resets currentTurnIndex to 0', () => {
    const room = makeRoomWithPlayers(5, 1)
    assignRoles(room)

    // turnOrder must contain all player IDs (same set, potentially different order)
    const originalIds = Array.from(room.players.keys()).sort()
    expect(room.turnOrder.slice().sort()).toEqual(originalIds)
    expect(room.currentTurnIndex).toBe(0)
  })

  it('works correctly with minimum 2 players (1 impostor, 1 civil)', () => {
    const room = makeRoomWithPlayers(2, 1)
    assignRoles(room)

    const roles = Array.from(room.players.values()).map((p) => p.role)
    expect(roles).toContain('impostor')
    expect(roles).toContain('civil')
  })

  it('does not assign more impostors than players-1 even if config requests it', () => {
    // Config says 5 impostors but there are only 3 players → max allowed = 2
    const room = makeRoomWithPlayers(3, 5)
    assignRoles(room)

    const impostors = Array.from(room.players.values()).filter((p) => p.role === 'impostor')
    // Should be capped at playerCount - 1 = 2
    expect(impostors.length).toBeLessThanOrEqual(2)
    // At least 1 civil must always exist
    const civiles = Array.from(room.players.values()).filter((p) => p.role === 'civil')
    expect(civiles.length).toBeGreaterThanOrEqual(1)
  })

  it('caps impostorCount at playerCount-1 exactly for edge config', () => {
    // 4 players, config asks for 10 → should cap at 3
    const room = makeRoomWithPlayers(4, 10)
    assignRoles(room)

    const impostors = Array.from(room.players.values()).filter((p) => p.role === 'impostor')
    expect(impostors).toHaveLength(3)
  })

  it('marks all players as isAlive=true after assignment', () => {
    const room = makeRoomWithPlayers(4, 1)
    // Simulate a player that was previously dead
    const firstPlayer = room.players.values().next().value!
    firstPlayer.isAlive = false

    assignRoles(room)

    for (const player of room.players.values()) {
      expect(player.isAlive).toBe(true)
    }
  })

  it('throws when room has no config', () => {
    const room = makeRoom({ config: null })

    expect(() => assignRoles(room)).toThrow('Cannot assign roles without game config')
  })

  it('produces different turnOrder arrangements across multiple calls (statistical)', () => {
    // Run 20 times on a 5-player room and verify at least one shuffled result differs
    const ordersSet = new Set<string>()
    for (let i = 0; i < 20; i++) {
      const room = makeRoomWithPlayers(5, 1)
      assignRoles(room)
      ordersSet.add(room.turnOrder.join(','))
    }
    // With 5 players, 5! = 120 possible orders; 20 runs should produce >1 unique order
    expect(ordersSet.size).toBeGreaterThan(1)
  })
})

// ---------------------------------------------------------------------------
// getNextTurnIndex
// ---------------------------------------------------------------------------

describe('getNextTurnIndex', () => {
  it('advances to the right (increment) by default', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1')],
        ['p2', makePlayer('p2', 'P2')],
        ['p3', makePlayer('p3', 'P3')],
      ]),
      turnOrder: ['p1', 'p2', 'p3'],
      currentTurnIndex: 0,
      turnDirection: 'right',
      eliminatedIds: new Set(),
    })

    expect(getNextTurnIndex(room)).toBe(1)
  })

  it('advances to the left (decrement) when direction is left', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1')],
        ['p2', makePlayer('p2', 'P2')],
        ['p3', makePlayer('p3', 'P3')],
      ]),
      turnOrder: ['p1', 'p2', 'p3'],
      currentTurnIndex: 0,
      turnDirection: 'left',
      eliminatedIds: new Set(),
    })

    // From index 0 going left wraps to index 2
    expect(getNextTurnIndex(room)).toBe(2)
  })

  it('wraps around to index 0 when advancing right past the last player', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1')],
        ['p2', makePlayer('p2', 'P2')],
        ['p3', makePlayer('p3', 'P3')],
      ]),
      turnOrder: ['p1', 'p2', 'p3'],
      currentTurnIndex: 2,
      turnDirection: 'right',
      eliminatedIds: new Set(),
    })

    expect(getNextTurnIndex(room)).toBe(0)
  })

  it('wraps around to last index when advancing left from index 0', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1')],
        ['p2', makePlayer('p2', 'P2')],
        ['p3', makePlayer('p3', 'P3')],
      ]),
      turnOrder: ['p1', 'p2', 'p3'],
      currentTurnIndex: 0,
      turnDirection: 'left',
      eliminatedIds: new Set(),
    })

    expect(getNextTurnIndex(room)).toBe(2)
  })

  it('skips players that are in eliminatedIds when going right', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1')],
        ['p2', makePlayer('p2', 'P2', { isAlive: false })],
        ['p3', makePlayer('p3', 'P3')],
      ]),
      turnOrder: ['p1', 'p2', 'p3'],
      currentTurnIndex: 0,
      turnDirection: 'right',
      eliminatedIds: new Set(['p2']),
    })

    // p2 is eliminated → should skip to p3 at index 2
    expect(getNextTurnIndex(room)).toBe(2)
  })

  it('skips players that have isAlive=false when going right', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1')],
        ['p2', makePlayer('p2', 'P2', { isAlive: false })],
        ['p3', makePlayer('p3', 'P3')],
      ]),
      turnOrder: ['p1', 'p2', 'p3'],
      currentTurnIndex: 0,
      turnDirection: 'right',
      eliminatedIds: new Set(),
    })

    // p2.isAlive is false → skip to p3
    expect(getNextTurnIndex(room)).toBe(2)
  })

  it('skips multiple consecutive eliminated players', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1')],
        ['p2', makePlayer('p2', 'P2', { isAlive: false })],
        ['p3', makePlayer('p3', 'P3', { isAlive: false })],
        ['p4', makePlayer('p4', 'P4')],
      ]),
      turnOrder: ['p1', 'p2', 'p3', 'p4'],
      currentTurnIndex: 0,
      turnDirection: 'right',
      eliminatedIds: new Set(['p2', 'p3']),
    })

    expect(getNextTurnIndex(room)).toBe(3)
  })

  it('returns currentTurnIndex when all players are eliminated (no valid next)', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { isAlive: false })],
        ['p2', makePlayer('p2', 'P2', { isAlive: false })],
      ]),
      turnOrder: ['p1', 'p2'],
      currentTurnIndex: 0,
      turnDirection: 'right',
      eliminatedIds: new Set(['p1', 'p2']),
    })

    expect(getNextTurnIndex(room)).toBe(0)
  })

  it('skips eliminated players going left', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1')],
        ['p2', makePlayer('p2', 'P2', { isAlive: false })],
        ['p3', makePlayer('p3', 'P3')],
      ]),
      turnOrder: ['p1', 'p2', 'p3'],
      currentTurnIndex: 2,
      turnDirection: 'left',
      eliminatedIds: new Set(['p2']),
    })

    // Going left from p3 (index 2): p2 is eliminated → skip to p1 (index 0)
    expect(getNextTurnIndex(room)).toBe(0)
  })
})

// ---------------------------------------------------------------------------
// resolveVotes
// ---------------------------------------------------------------------------

describe('resolveVotes', () => {
  it('eliminates the player with the most votes', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
        ['p2', makePlayer('p2', 'P2', { role: 'civil' })],
        ['p3', makePlayer('p3', 'P3', { role: 'impostor' })],
      ]),
      // p1 and p2 vote for p3, p3 votes for p1
      votes: new Map([
        ['p1', 'p3'],
        ['p2', 'p3'],
        ['p3', 'p1'],
      ]),
      eliminatedIds: new Set(),
    })

    const result = resolveVotes(room)

    expect(result.eliminatedId).toBe('p3')
    expect(result.eliminatedName).toBe('P3')
    expect(result.eliminatedRole).toBe('impostor')
  })

  it('marks the eliminated player as isAlive=false', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
        ['p2', makePlayer('p2', 'P2', { role: 'civil' })],
        ['p3', makePlayer('p3', 'P3', { role: 'impostor' })],
      ]),
      votes: new Map([['p1', 'p3'], ['p2', 'p3']]),
      eliminatedIds: new Set(),
    })

    resolveVotes(room)

    expect(room.players.get('p3')!.isAlive).toBe(false)
  })

  it('adds the eliminated player to room.eliminatedIds', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
      ]),
      votes: new Map([['p1', 'p2']]),
      eliminatedIds: new Set(),
    })

    resolveVotes(room)

    expect(room.eliminatedIds.has('p2')).toBe(true)
  })

  it('returns winner=civiles when the last impostor is eliminated', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
      ]),
      votes: new Map([['p1', 'p2']]),
      eliminatedIds: new Set(),
    })

    const result = resolveVotes(room)

    expect(result.winner).toBe('civiles')
  })

  it('does not set winner when a civil is eliminated', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
        ['p3', makePlayer('p3', 'P3', { role: 'civil' })],
      ]),
      votes: new Map([['p1', 'p3'], ['p2', 'p3']]),
      eliminatedIds: new Set(),
    })

    const result = resolveVotes(room)

    expect(result.winner).toBeUndefined()
  })

  it('returns no winner when an impostor is eliminated but other impostors survive', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
        ['p3', makePlayer('p3', 'P3', { role: 'impostor' })],
      ]),
      votes: new Map([['p1', 'p2']]),
      eliminatedIds: new Set(),
    })

    const result = resolveVotes(room)

    expect(result.winner).toBeUndefined()
  })

  it('returns null eliminatedId on a tie (two players with equal votes)', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
        ['p3', makePlayer('p3', 'P3', { role: 'civil' })],
      ]),
      // p1 votes p2, p2 votes p1 → tie between p1 and p2
      votes: new Map([
        ['p1', 'p2'],
        ['p2', 'p1'],
      ]),
      eliminatedIds: new Set(),
    })

    const result = resolveVotes(room)

    expect(result.eliminatedId).toBeNull()
    expect(result.eliminatedName).toBeNull()
    expect(result.eliminatedRole).toBeNull()
  })

  it('does not mark anyone as eliminated on a tie', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
      ]),
      votes: new Map([['p1', 'p2'], ['p2', 'p1']]),
      eliminatedIds: new Set(),
    })

    resolveVotes(room)

    expect(room.eliminatedIds.size).toBe(0)
    expect(room.players.get('p1')!.isAlive).toBe(true)
    expect(room.players.get('p2')!.isAlive).toBe(true)
  })

  it('returns correct votes record mapping voterId→targetId', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
      ]),
      votes: new Map([['p1', 'p2'], ['p2', 'p1']]),
      eliminatedIds: new Set(),
    })

    const result = resolveVotes(room)

    expect(result.votes).toEqual({ p1: 'p2', p2: 'p1' })
  })

  it('handles empty votes map (no votes → tie at 0)', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil' })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor' })],
      ]),
      votes: new Map(),
      eliminatedIds: new Set(),
    })

    const result = resolveVotes(room)

    // No candidates → nobody eliminated
    expect(result.eliminatedId).toBeNull()
    expect(result.votes).toEqual({})
  })
})

// ---------------------------------------------------------------------------
// checkVictory
// ---------------------------------------------------------------------------

describe('checkVictory', () => {
  it("returns 'civiles' when all impostors are eliminated", () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: false })],
      ]),
      config: { impostorCount: 1, rounds: 3, categoryId: 'cat-1', categoryName: 'Test', difficulty: 'hard' },
      currentRound: 1,
    })

    expect(checkVictory(room)).toBe('civiles')
  })

  it("returns 'impostores' when all rounds are exhausted and impostors survive", () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: true })],
      ]),
      config: { impostorCount: 1, rounds: 3, categoryId: 'cat-1', categoryName: 'Test', difficulty: 'hard' },
      currentRound: 3, // at final round
    })

    expect(checkVictory(room)).toBe('impostores')
  })

  it('returns null when impostors alive and rounds remain', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: true })],
      ]),
      config: { impostorCount: 1, rounds: 3, categoryId: 'cat-1', categoryName: 'Test', difficulty: 'hard' },
      currentRound: 1,
    })

    expect(checkVictory(room)).toBeNull()
  })

  it("returns 'civiles' even if rounds are exhausted when no impostors are alive", () => {
    // civiles win condition takes priority
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: false })],
      ]),
      config: { impostorCount: 1, rounds: 3, categoryId: 'cat-1', categoryName: 'Test', difficulty: 'hard' },
      currentRound: 3,
    })

    expect(checkVictory(room)).toBe('civiles')
  })

  it('returns null when currentRound is below total rounds and impostors are alive', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: true })],
        ['p3', makePlayer('p3', 'P3', { role: 'civil', isAlive: true })],
      ]),
      config: { impostorCount: 1, rounds: 3, categoryId: 'cat-1', categoryName: 'Test', difficulty: 'hard' },
      currentRound: 2,
    })

    expect(checkVictory(room)).toBeNull()
  })

  it('returns null when no config is present and impostors are alive', () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: true })],
      ]),
      config: null,
      currentRound: 99,
    })

    // No config → cannot determine round victory → returns null
    expect(checkVictory(room)).toBeNull()
  })

  it("returns 'impostores' exactly at currentRound === config.rounds", () => {
    const room = makeRoom({
      players: new Map([
        ['p1', makePlayer('p1', 'P1', { role: 'civil', isAlive: true })],
        ['p2', makePlayer('p2', 'P2', { role: 'impostor', isAlive: true })],
      ]),
      config: { impostorCount: 1, rounds: 5, categoryId: 'cat-1', categoryName: 'Test', difficulty: 'hard' },
      currentRound: 5,
    })

    expect(checkVictory(room)).toBe('impostores')
  })
})
