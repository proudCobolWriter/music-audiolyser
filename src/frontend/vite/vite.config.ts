import { defineConfig, UserConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
/** @type {import('vite').UserConfig} */
export default defineConfig({
  base: "/static/",
  build: {
    manifest: "manifest.json",
    outDir: "./assets",
    rollupOptions: {
      //input: "/path/to/main.js"
    }
  },
  plugins: [react()],
}) satisfies UserConfig
