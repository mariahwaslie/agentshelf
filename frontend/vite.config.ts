import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const backend = "http://localhost:8000";

// The dev server forwards backend paths to FastAPI, so the app uses same-origin URLs everywhere.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": backend, "/health": backend, "/webhooks": backend },
  },
});
