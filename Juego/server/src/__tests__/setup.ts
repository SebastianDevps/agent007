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

import Module from 'module'
import path from 'path'

// ESM import — Vitest's loader ensures this is the singleton instance.
import * as roomStore from '../rooms/room.store'

// ── Inject store into Node CJS require cache ────────────────────────────────
const STORE_ABS = path.resolve(__dirname, '../rooms/room.store.ts')

function makeFakeModule(filename: string, exports: unknown) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mod = new (Module as any)(filename, null)
  mod.exports = exports
  mod.loaded = true
  mod.filename = filename
  mod.id = filename
  return mod
}

// Register under the exact key that _resolveFilename will produce for .ts
if (!require.cache[STORE_ABS]) {
  require.cache[STORE_ABS] = makeFakeModule(STORE_ABS, roomStore)
}

// ── Patch _resolveFilename to redirect require('…/room.store') ─────────────
const _orig = (Module as any)._resolveFilename as (
  request: string,
  parent: NodeJS.Module | null,
  isMain: boolean,
  options?: object
) => string

;(Module as any)._resolveFilename = function (
  request: string,
  parent: NodeJS.Module | null | { filename?: string },
  isMain: boolean,
  options?: object
): string {
  // Only intercept room.store requests from handler files
  if (request.endsWith('/room.store') || request === '../rooms/room.store') {
    const parentFile = (parent as { filename?: string })?.filename ?? ''
    if (parentFile.includes('/handlers/') || parentFile.includes('handler')) {
      return STORE_ABS
    }
  }
  return _orig.call(this, request, parent as NodeJS.Module, isMain, options)
}
