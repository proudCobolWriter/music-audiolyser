import { resolve } from "path";

import { defineConfig, type UserConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// @ts-ignore
const getFileExtension = (filename: string): string => {
    return filename.split(".").pop() || "";
};

const img_mime_formats = [
    "gif",
    "hdp",
    "wdp",
    "jpe",
    "jpg",
    "jpeg",
    "png",
    "svg",
    "tiff",
    "tif",
    "bmp",
    "dib",
    "cal",
    "cals",
    "mil",
    "afp",
    "jb2",
    "jbig2",
    "jp2",
    "jpf",
    "pcx",
    "dcx",
    "list",
    "lst",
    "tpdf",
    "pzm",
]; // all possible image file formats for better organisation in dist, all images are grouped in one single img/ folder later down the line

// https://vite.dev/config/
/** @type {import('vite').UserConfig} */
export default defineConfig(
    // @ts-ignore to keep all the following arguments for easier configuring
    ({ command, mode, isSsrBuild, isPreview }) =>
        ({
            base: mode === "production" ? "/static/" : "/", // default redirect url (home)
            root: "./", // the index.html file should be here basically
            publicDir: "./public", // redundancy
            build: {
                minify: true,
                emptyOutDir: true,
                manifest: "manifest.json",
                assetsInlineLimit: 0,
                outDir: resolve(__dirname, "dist"),
                rollupOptions: {
                    input: {
                        main: resolve(__dirname, "src", "main.tsx"),
                    },
                    output: {
                        entryFileNames: () => "assets/js/[name]-[hash].js",
                        chunkFileNames: () => {
                            return "assets/js/[name]-[hash].js";
                        },
                        assetFileNames: (assetInfo) => {
                            const ext = getFileExtension(assetInfo.names[0]);
                            return `assets/${ext === "css" ? "css/" : img_mime_formats.some((x) => x === ext) ? "img/" : ""}[name].[ext]`;
                        },
                    },
                    watch: {
                        // https://rollupjs.org/configuration-options/#watch
                    },
                },
            },
            server: {
                port: 5173,
                strictPort: true, // or else django-vite wouldn't work in development mode, disable if not necessary
                host: "0.0.0.0", // Listen on all network interfaces to make it work on both localhost and 127.0.0.1
                proxy: {
                    // request forwarding for development
                    "/admin": {
                        target: "http://127.0.0.1:8000/",
                        changeOrigin: true,
                        secure: true,
                    },
                    "/static": {
                        target: "http://127.0.0.1:8000/",
                        changeOrigin: true,
                        secure: false,
                    },
                },
            },
            plugins: [react()],
        }) satisfies UserConfig,
);
