"use strict";
/**
 * setup.ts — Vitest global setup file
 *
 * Problem: The handler files use `require('../rooms/room.store')` dynamically
 * inside `findSocketRoom`. Vitest 4 uses its own module loader for ESM/TS
 * files, giving them a separate registry from Node's native CJS `require`
 * cache.  When the dynamic `require` fires it creates a *new* `rooms` Map —
 * empty — so `findSocketRoom` never finds any room.
 *
 * Fix: intercept `Module._resolveFilename`.  When Node is asked to resolve
 * `'../rooms/room.store'` (or any variant) from a file inside `src/handlers/`,
 * we redirect to the absolute path we injected into `require.cache` with the
 * real (Vitest-loaded) module exports.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const module_1 = __importDefault(require("module"));
const path_1 = __importDefault(require("path"));
// ESM import — Vitest's loader ensures this is the singleton instance.
const roomStore = __importStar(require("../rooms/room.store"));
// ── Inject store into Node CJS require cache ────────────────────────────────
const STORE_ABS = path_1.default.resolve(__dirname, '../rooms/room.store.ts');
function makeFakeModule(filename, exports) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const mod = new module_1.default(filename, null);
    mod.exports = exports;
    mod.loaded = true;
    mod.filename = filename;
    mod.id = filename;
    return mod;
}
// Register under the exact key that _resolveFilename will produce for .ts
if (!require.cache[STORE_ABS]) {
    require.cache[STORE_ABS] = makeFakeModule(STORE_ABS, roomStore);
}
// ── Patch _resolveFilename to redirect require('…/room.store') ─────────────
const _orig = module_1.default._resolveFilename;
module_1.default._resolveFilename = function (request, parent, isMain, options) {
    // Only intercept room.store requests from handler files
    if (request.endsWith('/room.store') || request === '../rooms/room.store') {
        const parentFile = parent?.filename ?? '';
        if (parentFile.includes('/handlers/') || parentFile.includes('handler')) {
            return STORE_ABS;
        }
    }
    return _orig.call(this, request, parent, isMain, options);
};
