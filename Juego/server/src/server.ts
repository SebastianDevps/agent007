import 'dotenv/config'
import express from 'express'
import { createServer } from 'http'
import { Server } from 'socket.io'
import cors from 'cors'
import { registerLobbyHandlers } from './handlers/lobby.handler'
import { registerClueHandlers } from './handlers/clue.handler'
import { registerVoteHandlers } from './handlers/vote.handler'
import { registerConnectionHandlers } from './handlers/connection.handler'
import { getActiveCategories } from './words/word.service'

const PORT = process.env.PORT ?? 3001
const CLIENT_URL = process.env.CLIENT_URL ?? 'http://localhost:5173'

const app = express()
app.use(cors({ origin: CLIENT_URL }))
app.use(express.json())

const httpServer = createServer(app)
const io = new Server(httpServer, {
  cors: { origin: CLIENT_URL, methods: ['GET', 'POST'] },
})

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' })
})

app.get('/api/categories', async (_req, res) => {
  try {
    const categories = await getActiveCategories()
    res.json(categories)
  } catch (error) {
    console.error('[api] categories error:', error)
    res.status(500).json({ error: 'Failed to fetch categories' })
  }
})

io.on('connection', (socket) => {
  console.log(`[+] connected: ${socket.id}`)

  registerLobbyHandlers(socket, io)
  registerClueHandlers(socket, io)
  registerVoteHandlers(socket, io)
  registerConnectionHandlers(socket, io)
})

httpServer.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`)
})

export { io }
