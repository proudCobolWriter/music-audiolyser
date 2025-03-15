import { defineConfig, UserConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
/** @type {import('vite').UserConfig} */
export default defineConfig({
  base: "./",
  plugins: [react()],
  build: {
    manifest: "manifest.json",
    outDir: "./dist",
    rollupOptions: {
      //input: "/path/to/main.js"
      output: {
        assetFileNames: () => {
          return "assets/css/index.min.css"
        },
        entryFileNames: () => {
          return "assets/js/[name].min.css"
        },
      }
    }
  },
}) satisfies UserConfig
