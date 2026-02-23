export type Role = 'civil' | 'impostor'

export type GamePhase =
  | 'lobby'
  | 'reveal'
  | 'clue-phase'
  | 'voting'
  | 'round-end'
  | 'game-over'

export type TurnDirection = 'left' | 'right'

export type Winner = 'civiles' | 'impostores'

export interface Player {
  id: string            // socket.id (cambia en reconexión)
  name: string
  role: Role | null
  isAlive: boolean
  sessionToken: string  // estable entre recargas
}

export interface GameConfig {
  impostorCount: number
  rounds: number
  categoryId: string
  categoryName: string
  difficulty: 'easy' | 'hard'
}

export interface Room {
  code: string
  hostId: string
  phase: GamePhase
  players: Map<string, Player>
  config: GameConfig | null
  word: string | null         // civiles ven esto
  referenceWord: string | null // impostores ven esto
  hint: string | null
  currentRound: number
  turnOrder: string[]         // socket.ids ordenados
  currentTurnIndex: number
  turnDirection: TurnDirection
  clues: Map<string, string>  // playerId → clue
  votes: Map<string, string>  // voterId → targetId
  eliminatedIds: Set<string>
  readyPlayers: Set<string>           // jugadores que ya vieron su rol
  readyTimeout: NodeJS.Timeout | null // fallback si alguno no confirma
}
