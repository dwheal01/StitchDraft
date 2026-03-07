import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Align HMR WebSocket with the page origin so localhost vs 127.0.0.1 doesn't break WS.
    hmr: { host: 'localhost', port: 5173 },
    // Proxy /preview to the backend so the browser uses same origin (avoids CORS in dev).
    proxy: {
      '/preview': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
