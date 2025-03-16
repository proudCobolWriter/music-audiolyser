import { resolve } from "path";

import { defineConfig, type UserConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vite.dev/config/
/** @type {import('vite').UserConfig} */
export default defineConfig({
    base: "/static/",
    build: {
        manifest: "manifest.json",
        outDir: "./dist",
        rollupOptions: {
            //input: "/path/to/main.js"
            input: {
                main: resolve(__dirname, "index.html"),
            },
            output: {
                entryFileNames: "[name].js",
                assetFileNames: "assets/[name].[ext]",
            },
        },
    },
    plugins: [react()],
}) satisfies UserConfig;
