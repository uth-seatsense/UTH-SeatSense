import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    include: [
      "src/tests/**/*.test.{js,jsx,ts,tsx}",
      "tests/**/*.test.{js,jsx,ts,tsx}",
    ],
  },
  server: {
    host: "0.0.0.0",
    watch: {
      usePolling: true,
      interval: 1000,
    },
    hmr: {
      host: 'localhost',
    },
    proxy: {
      "/api": {
        target: process.env.VITE_BACKEND_PROXY_TARGET ?? "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
