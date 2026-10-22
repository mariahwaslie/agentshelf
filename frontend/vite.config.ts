import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// 127.0.0.1, not localhost: localhost can resolve to IPv6 ::1, where another service may own :8000.
const backend = "http://127.0.0.1:8000";

// The dev server forwards backend paths to FastAPI, so the app uses same-origin URLs everywhere.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": backend, "/health": backend, "/webhooks": backend },
  },
});
