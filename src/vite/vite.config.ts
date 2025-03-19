import { resolve } from "path";

import { defineConfig, type UserConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vite.dev/config/
/** @type {import('vite').UserConfig} */
export default defineConfig({
    base: "/static/",
    build: {
        minify: true,
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
            watch: {
                // https://rollupjs.org/configuration-options/#watch
            },
        },
    },
    server: {
        host: "0.0.0.0", // Listen on all network interfaces to make it work on both localhost and 127.0.0.1
    },
    plugins: [react()],
}) satisfies UserConfig;
