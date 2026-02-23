/**
 * game.e2e.test.ts
 *
 * Integration E2E tests for "El Impostor" Socket.IO server.
 * Spins up a real HTTP + Socket.IO server on a random port and connects
 * real socket.io-client instances to exercise the full event pipeline.
 *
 * Run: vitest run src/__tests__/game.e2e.test.ts
 */

import { createServer } from 'http'
import { Server } from 'socket.io'
import { io as ioc, type Socket as ClientSocket } from 'socket.io-client'
import express from 'express'
import cors from 'cors'
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest'

// ---------------------------------------------------------------------------
// Mock word.service so start-game never touches Supabase
// ---------------------------------------------------------------------------
vi.mock('../words/word.service', () => ({
  getActiveCategories: vi.fn().mockResolvedValue([
    { id: 'cat-1', name: 'Test', emoji: '🧪' },
  ]),
  getRandomWordPair: vi.fn().mockResolvedValue({ word: 'perro', ref: 'lobo' }),
}))

// ---------------------------------------------------------------------------
// Handlers (imported AFTER the mock above is in place)
// ---------------------------------------------------------------------------
import { registerLobbyHandlers } from '../handlers/lobby.handler'
import { registerClueHandlers } from '../handlers/clue.handler'
import { registerVoteHandlers } from '../handlers/vote.handler'
import { registerConnectionHandlers } from '../handlers/connection.handler'

// ---------------------------------------------------------------------------
// Server bootstrap helpers
// ---------------------------------------------------------------------------

interface TestServer {
  io: Server
  url: string
  close: () => Promise<void>
}

function buildTestServer(): Promise<TestServer> {
  return new Promise((resolve, reject) => {
    const app = express()
    app.use(cors())
    app.use(express.json())

    const httpServer = createServer(app)
    const io = new Server(httpServer, {
      cors: { origin: '*', methods: ['GET', 'POST'] },
      // Reduce polling overhead in tests
      transports: ['websocket'],
    })

    io.on('connection', (socket) => {
      registerLobbyHandlers(socket, io)
      registerClueHandlers(socket, io)
      registerVoteHandlers(socket, io)
      registerConnectionHandlers(socket, io)
    })

    httpServer.listen(0, () => {
      const addr = httpServer.address()
      if (!addr || typeof addr === 'string') {
        reject(new Error('Could not determine server address'))
        return
      }
      const url = `http://localhost:${addr.port}`

      resolve({
        io,
        url,
        close: () =>
          new Promise<void>((res) => {
            // io.close() closes all sockets AND the underlying HTTP server.
            // Calling httpServer.close() again after would throw ERR_SERVER_NOT_RUNNING.
            io.close(() => res())
          }),
      })
    })
  })
}

function makeClient(url: string): ClientSocket {
  return ioc(url, {
    transports: ['websocket'],
    autoConnect: false,
  })
}

function connect(socket: ClientSocket): Promise<void> {
  return new Promise((resolve, reject) => {
    socket.once('connect', resolve)
    socket.once('connect_error', reject)
    socket.connect()
  })
}

function waitFor<T>(socket: ClientSocket, event: string): Promise<T> {
  return new Promise((resolve) => socket.once(event, resolve))
}

function disconnectAll(...sockets: ClientSocket[]): Promise<void[]> {
  return Promise.all(
    sockets.map(
      (s) =>
        new Promise<void>((resolve) => {
          if (!s.connected) {
            resolve()
            return
          }
          s.once('disconnect', () => resolve())
          s.disconnect()
        })
    )
  )
}

// ---------------------------------------------------------------------------
// Test-level types
// ---------------------------------------------------------------------------

interface SerializedPlayer {
  id: string
  name: string
  isHost: boolean
  isAlive: boolean
  isEliminated: boolean
}

// ---------------------------------------------------------------------------
// Global server shared across all suites
// ---------------------------------------------------------------------------

let server: TestServer

beforeAll(async () => {
  server = await buildTestServer()
})

afterAll(async () => {
  await server.close()
})

// ===========================================================================
// Suite: Lobby flow
// ===========================================================================

describe('Lobby flow', () => {
  let host: ClientSocket
  let guest: ClientSocket

  beforeEach(async () => {
    host = makeClient(server.url)
    guest = makeClient(server.url)
    await connect(host)
  })

  afterEach(async () => {
    await disconnectAll(host, guest)
  })

  it('crear sala y recibir code', async () => {
    const code = await new Promise<string>((resolve) => {
      host.emit('create-room', 'Alice', (code: string) => resolve(code))
    })

    expect(typeof code).toBe('string')
    expect(code).toHaveLength(6)
    // nanoid uses URL-safe alphabet — all uppercase after toUpperCase()
    expect(code).toMatch(/^[A-Z0-9_-]{6}$/)
  })

  it('unirse a sala existente — ambos reciben room-updated con 2 jugadores', async () => {
    await connect(guest)

    const code = await new Promise<string>((resolve) => {
      host.emit('create-room', 'Alice', resolve)
    })

    // After host creates room, both clients should ultimately see 2 players.
    // We listen for room-updated on host BEFORE guest joins.
    const roomUpdatedPromise = waitFor<SerializedPlayer[]>(host, 'room-updated')

    const err = await new Promise<string | undefined>((resolve) => {
      guest.emit('join-room', { code, name: 'Bob' }, resolve)
    })

    expect(err).toBeUndefined()

    // Host receives room-updated with 2 players
    const players = await roomUpdatedPromise
    expect(players).toHaveLength(2)
    const names = players.map((p) => p.name)
    expect(names).toContain('Alice')
    expect(names).toContain('Bob')
    expect(players.find((p) => p.name === 'Alice')?.isHost).toBe(true)
  })

  it('error al unirse a sala inexistente — callback con ROOM_NOT_FOUND', async () => {
    await connect(guest)

    const err = await new Promise<string | undefined>((resolve) => {
      guest.emit('join-room', { code: 'XXXXXX', name: 'Charlie' }, resolve)
    })

    expect(err).toBe('ROOM_NOT_FOUND')
  })

  it('error al unirse a partida en curso — callback con GAME_STARTED', async () => {
    await connect(guest)

    // Create room and start game manually by manipulating state via a second
    // client that also joins, then we trigger start-game. We need at least 2
    // players, so we use a third socket.
    const third = makeClient(server.url)
    await connect(third)

    const code = await new Promise<string>((resolve) => {
      host.emit('create-room', 'Alice', resolve)
    })

    await new Promise<void>((resolve) => {
      third.emit('join-room', { code, name: 'Dave' }, () => resolve())
    })

    // Set config then start game
    host.emit('update-config', {
      impostorCount: 1,
      rounds: 1,
      categoryId: 'cat-1',
      categoryName: 'Test',
    })

    await new Promise<string | undefined>((resolve) => {
      host.emit('start-game', resolve)
    })

    // Now guest tries to join the in-progress room
    const err = await new Promise<string | undefined>((resolve) => {
      guest.emit('join-room', { code, name: 'Lateomer' }, resolve)
    })

    expect(err).toBe('GAME_STARTED')
    await disconnectAll(third)
  })

  it('solo el host puede actualizar config — non-host no emite config-updated', async () => {
    await connect(guest)

    const code = await new Promise<string>((resolve) => {
      host.emit('create-room', 'Alice', resolve)
    })

    await new Promise<void>((resolve) => {
      guest.emit('join-room', { code, name: 'Bob' }, () => resolve())
    })

    // Listen for config-updated — should NOT arrive
    let configReceived = false
    host.on('config-updated', () => {
      configReceived = true
    })
    guest.on('config-updated', () => {
      configReceived = true
    })

    guest.emit('update-config', {
      impostorCount: 1,
      rounds: 1,
      categoryId: 'cat-1',
      categoryName: 'Test',
    })

    // Wait a short time to ensure no event arrives
    await new Promise((r) => setTimeout(r, 150))
    expect(configReceived).toBe(false)
  })

  it('config-updated llega a todos — host actualiza, todos reciben el evento', async () => {
    await connect(guest)

    const code = await new Promise<string>((resolve) => {
      host.emit('create-room', 'Alice', resolve)
    })

    await new Promise<void>((resolve) => {
      guest.emit('join-room', { code, name: 'Bob' }, () => resolve())
    })

    const config = {
      impostorCount: 1,
      rounds: 2,
      categoryId: 'cat-1',
      categoryName: 'Test',
    }

    const [hostConfig, guestConfig] = await Promise.all([
      waitFor(host, 'config-updated'),
      waitFor(guest, 'config-updated'),
      // Emit after listeners are registered
      new Promise<void>((r) => {
        setTimeout(() => {
          host.emit('update-config', config)
          r()
        }, 10)
      }),
    ])

    expect(hostConfig).toEqual(config)
    expect(guestConfig).toEqual(config)
  })
})

// ===========================================================================
// Suite: Game flow (2 jugadores)
// ===========================================================================

describe('Game flow (2 jugadores)', () => {
  let host: ClientSocket
  let guest: ClientSocket
  let roomCode: string

  beforeEach(async () => {
    host = makeClient(server.url)
    guest = makeClient(server.url)
    await connect(host)
    await connect(guest)

    roomCode = await new Promise<string>((resolve) => {
      host.emit('create-room', 'Alice', resolve)
    })

    await new Promise<void>((resolve) => {
      guest.emit('join-room', { code: roomCode, name: 'Bob' }, () => resolve())
    })
  })

  afterEach(async () => {
    await disconnectAll(host, guest)
  })

  it('flujo completo de partida', async () => {
    // ------------------------------------------------------------------
    // 1. update-config
    // ------------------------------------------------------------------
    const config = {
      impostorCount: 1,
      rounds: 1,
      categoryId: 'cat-1',
      categoryName: 'Test',
    }
    host.emit('update-config', config)
    await new Promise((r) => setTimeout(r, 30))

    // ------------------------------------------------------------------
    // 2. start-game → game-started + role-assigned (×2) + turn-started
    // ------------------------------------------------------------------
    const hostGameStarted = waitFor(host, 'game-started')
    const guestGameStarted = waitFor(guest, 'game-started')
    const hostRole = waitFor<{ role: string; word: string }>(host, 'role-assigned')
    const guestRole = waitFor<{ role: string; word: string }>(guest, 'role-assigned')
    const firstTurn = waitFor<{ playerId: string; direction: string; round: number }>(
      host,
      'turn-started'
    )

    const startError = await new Promise<string | undefined>((resolve) => {
      host.emit('start-game', resolve)
    })
    expect(startError).toBeUndefined()

    await Promise.all([hostGameStarted, guestGameStarted])

    const [hr, gr] = await Promise.all([hostRole, guestRole])
    expect(['civil', 'impostor']).toContain(hr.role)
    expect(['civil', 'impostor']).toContain(gr.role)
    // Exactly one impostor in a 2-player game with impostorCount=1
    const roles = [hr.role, gr.role]
    expect(roles.filter((r) => r === 'impostor')).toHaveLength(1)
    // civil gets real word, impostor gets reference word
    expect(typeof hr.word).toBe('string')
    expect(hr.word.length).toBeGreaterThan(0)

    const turn = await firstTurn
    expect(turn).toMatchObject({
      direction: expect.stringMatching(/^(left|right)$/),
      round: 1,
    })
    expect(typeof turn.playerId).toBe('string')

    // ------------------------------------------------------------------
    // 3. clue phase — figure out who goes first
    // ------------------------------------------------------------------
    const firstPlayerId = turn.playerId
    // Map socket.id → ClientSocket
    const socketById: Record<string, ClientSocket> = {
      [host.id as string]: host,
      [guest.id as string]: guest,
    }
    const firstSocket = socketById[firstPlayerId]
    const secondSocket = firstSocket === host ? guest : host

    // First player submits clue → clue-submitted + turn-started (not voting yet)
    const clue1Received = waitFor<{ playerId: string; playerName: string; clue: string }>(
      host,
      'clue-submitted'
    )
    firstSocket.emit('submit-clue', 'mi pista uno')
    const clue1 = await clue1Received
    expect(clue1.clue).toBe('mi pista uno')
    expect(clue1.playerId).toBe(firstPlayerId)

    // Second player submits clue → clue-submitted + voting-started
    const clue2Received = waitFor<{ playerId: string; clue: string }>(host, 'clue-submitted')
    const votingStartedHost = waitFor(host, 'voting-started')
    const votingStartedGuest = waitFor(guest, 'voting-started')

    secondSocket.emit('submit-clue', 'mi pista dos')
    await Promise.all([clue2Received, votingStartedHost, votingStartedGuest])

    // ------------------------------------------------------------------
    // 4. voting phase — both vote, first one votes for second and vice-versa
    // ------------------------------------------------------------------
    // vote-cast is broadcast to ALL players in the room, so each socket
    // receives N events (one per voter). We collect all N from a single
    // socket instead of using .once on each socket independently.
    const collectVoteCasts = (n: number): Promise<string[]> =>
      new Promise((resolve) => {
        const ids: string[] = []
        const handler = (voterId: string) => {
          ids.push(voterId)
          if (ids.length >= n) {
            host.off('vote-cast', handler)
            resolve(ids)
          }
        }
        host.on('vote-cast', handler)
      })

    const voteCastCollector = collectVoteCasts(2)

    const roundResultHost = waitFor<{
      eliminatedId: string | null
      round: number
      winner?: string
    }>(host, 'round-result')
    const roundResultGuest = waitFor<{
      eliminatedId: string | null
      round: number
    }>(guest, 'round-result')

    // Collect game-over or turn-started (whichever arrives)
    let gameOverPayload: unknown = null
    const gameOverOrNextTurn = new Promise<void>((resolve) => {
      host.once('game-over', (payload) => {
        gameOverPayload = payload
        resolve()
      })
      host.once('turn-started', () => resolve())
    })

    host.emit('submit-vote', guest.id)
    guest.emit('submit-vote', host.id)

    const castIds = await voteCastCollector
    // vote-cast emits the voterId — should be host.id and guest.id in some order
    expect(castIds).toEqual(expect.arrayContaining([host.id, guest.id]))

    const [resHost, resGuest] = await Promise.all([roundResultHost, roundResultGuest])
    expect(resHost.round).toBe(1)
    expect(resGuest.round).toBe(1)

    // With 2 players voting for each other it's a tie → no elimination,
    // but with 1 round config the game ends immediately after.
    await gameOverOrNextTurn

    // If game-over arrived, verify shape
    if (gameOverPayload !== null) {
      const payload = gameOverPayload as { winner: string; roles: Record<string, string>; word: string }
      expect(['civiles', 'impostores']).toContain(payload.winner)
      expect(typeof payload.word).toBe('string')
      expect(typeof payload.roles).toBe('object')
    }
  })
})

// ===========================================================================
// Suite: Edge cases
// ===========================================================================

describe('Edge cases', () => {
  let host: ClientSocket
  let guest: ClientSocket

  beforeEach(async () => {
    host = makeClient(server.url)
    guest = makeClient(server.url)
    await connect(host)
    await connect(guest)
  })

  afterEach(async () => {
    await disconnectAll(host, guest)
  })

  it('desconexión del host transfiere host al siguiente jugador', async () => {
    const code = await new Promise<string>((resolve) => {
      host.emit('create-room', 'Alice', resolve)
    })

    await new Promise<void>((resolve) => {
      guest.emit('join-room', { code, name: 'Bob' }, () => resolve())
    })

    // Listen for room-updated on guest after host disconnects
    const roomUpdatedAfterDisconnect = waitFor<SerializedPlayer[]>(guest, 'room-updated')

    host.disconnect()

    const players = await roomUpdatedAfterDisconnect

    // Only Bob remains
    expect(players).toHaveLength(1)
    expect(players[0].name).toBe('Bob')
    expect(players[0].isHost).toBe(true)
  })

  it('desconexión de jugador en sala vacía elimina la sala', async () => {
    // Single player creates room then disconnects
    const solo = makeClient(server.url)
    await connect(solo)

    const code = await new Promise<string>((resolve) => {
      solo.emit('create-room', 'Solo', resolve)
    })

    // Disconnect the only player
    await new Promise<void>((resolve) => {
      solo.once('disconnect', resolve)
      solo.disconnect()
    })

    // Give the server a tick to process the disconnect
    await new Promise((r) => setTimeout(r, 100))

    // A new client tries to join that room — should get ROOM_NOT_FOUND
    const newClient = makeClient(server.url)
    await connect(newClient)

    const err = await new Promise<string | undefined>((resolve) => {
      newClient.emit('join-room', { code, name: 'Latecomer' }, resolve)
    })

    expect(err).toBe('ROOM_NOT_FOUND')
    await disconnectAll(newClient)
  })
})
