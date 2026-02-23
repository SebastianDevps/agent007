import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'node',
    globals: true,
    // Give each test up to 15 s by default (E2E + stress suites need headroom)
    testTimeout: 15_000,
    // Run in the same worker process so module singletons (room store) are
    // shared between the test file and the handler code it imports.
    pool: 'forks',
    // Patch Node's CJS resolver to understand .ts extensions so that the
    // dynamic require('../rooms/room.store') calls inside handlers work.
    setupFiles: ['./src/__tests__/setup.ts'],
  },
})
