import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [react()],
  test: { environment: 'jsdom', include: ['src/**/*.ui.test.jsx'],
    setupFiles: ['./src/testSetup.js'], maxWorkers: 1, minWorkers: 1 },
})
