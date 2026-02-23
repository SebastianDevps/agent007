"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.io = void 0;
require("dotenv/config");
const express_1 = __importDefault(require("express"));
const http_1 = require("http");
const socket_io_1 = require("socket.io");
const cors_1 = __importDefault(require("cors"));
const lobby_handler_1 = require("./handlers/lobby.handler");
const clue_handler_1 = require("./handlers/clue.handler");
const vote_handler_1 = require("./handlers/vote.handler");
const connection_handler_1 = require("./handlers/connection.handler");
const word_service_1 = require("./words/word.service");
const PORT = process.env.PORT ?? 3001;
const CLIENT_URL = process.env.CLIENT_URL ?? 'http://localhost:5173';
const app = (0, express_1.default)();
app.use((0, cors_1.default)({ origin: CLIENT_URL }));
app.use(express_1.default.json());
const httpServer = (0, http_1.createServer)(app);
const io = new socket_io_1.Server(httpServer, {
    cors: { origin: CLIENT_URL, methods: ['GET', 'POST'] },
});
exports.io = io;
app.get('/health', (_req, res) => {
    res.json({ status: 'ok' });
});
app.get('/api/categories', async (_req, res) => {
    try {
        const categories = await (0, word_service_1.getActiveCategories)();
        res.json(categories);
    }
    catch (error) {
        console.error('[api] categories error:', error);
        res.status(500).json({ error: 'Failed to fetch categories' });
    }
});
io.on('connection', (socket) => {
    console.log(`[+] connected: ${socket.id}`);
    (0, lobby_handler_1.registerLobbyHandlers)(socket, io);
    (0, clue_handler_1.registerClueHandlers)(socket, io);
    (0, vote_handler_1.registerVoteHandlers)(socket, io);
    (0, connection_handler_1.registerConnectionHandlers)(socket, io);
});
httpServer.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
