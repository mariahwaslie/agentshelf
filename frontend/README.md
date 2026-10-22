# frontend/

React + Vite + TypeScript (strict). Served by FastAPI from `dist/` in production; in development `npm run dev` proxies `/api`, `/health` and `/webhooks` to the backend on :8000.

- **API calls** go through `src/api/client.ts` only.
- **API types** in `src/api/types.gen.ts` are generated from the backend's OpenAPI schema with `make types`. Never edit them by hand; `make check` fails if they are stale.
