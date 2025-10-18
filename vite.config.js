import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Vite needs to know about the PostCSS configuration for Tailwind to work
  css: {
    postcss: './postcss.config.js',
  },
  // Ensure the server starts on the correct port and host
  server: {
    port: 5173,
    host: true,
  }
});
