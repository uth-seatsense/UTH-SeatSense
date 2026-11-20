import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    // Chạy trong môi trường Node (server-side render với react-dom/server)
    environment: "node",
    include: ["src/tests/**/*.test.{js,jsx,ts,tsx}"],
  },
  server: {
    host: "0.0.0.0",
    proxy: {
      "/api": {
        target: process.env.VITE_BACKEND_PROXY_TARGET ?? "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
