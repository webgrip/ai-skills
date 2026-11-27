import { defineConfig } from "vite";

export default defineConfig({
  build: {
    outDir: "dist/harness",
    emptyOutDir: true,
    chunkSizeWarningLimit: 1024,
    rollupOptions: { input: "harness.html" },
  },
  preview: { port: 4173, strictPort: true },
});
