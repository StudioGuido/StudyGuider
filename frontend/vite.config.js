import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Load .env from project root so VITE_* vars from root .env are available
  envDir: path.resolve(__dirname, '..'),
})
