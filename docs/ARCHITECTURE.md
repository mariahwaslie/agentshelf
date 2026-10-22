# Architecture (confirmed in prompt 00; see `docs/decisions/0001-stack.md`)

```
                 ┌──────────────────────── Single Render web service (Docker) ────────────────────────┐
 Browser ──────► │  FastAPI (app factory: app.main:create_app)                                        │
 (React SPA      │   ├─ /api/*      routes (api/) ──► domain/ (catalog, benchmark, enrichment, ...)   │
  served by      │   ├─ /webhooks/paypal  ──► verify signature ─► idempotent handler                  │
  FastAPI)       │   ├─ /health                                                                       │
                 │   └─ /  (frontend/dist static files, index.html fallback)                          │
                 │                                                                                    │
                 │  clients/ ──httpx──► RecordReplayTransport (cache/) ──► trace/ (API Trace events)  │
                 │     paypal.py ──────────► PayPal Sandbox REST (Catalog, Orders v2, Webhooks,       │
                 │                           Shipment tracking, Transactions) [+ Agent Toolkit]       │
                 │     channel3.py ────────► Channel3 /v1/search                                     │
                 │     llm.py ─────────────► Gemini REST (free tier), temperature 0, JSON schema      │
                 │     embeddings.py ──────► fastembed (local ONNX; vectors cached by the same keys)  │
                 │                                                                                    │
                 │  db/ ── SQLAlchemy 2.0 ──► SQLite (seeded on boot; "Reset demo" restores "before") │
                 └────────────────────────────────────────────────────────────────────────────────────┘
 PayPal JS SDK v6 (buyer approval, PayPal + Pay Later buttons) runs in the browser.
```

## Backend packages
| Package | Responsibility |
|---|---|
| `api/` | One router per product area. Thin: validate, call domain, map to contract models. |
| `domain/` | Pure logic (ranking, metrics, grounding validation, diffing). No HTTP, no DB. |
| `clients/` | The **only** gateways to external services; each uses an `httpx.Client` with the record/replay transport. |
| `cache/` | Fixture key scheme (`keys.py`) and store interface (`store.py`); transport in prompt 02. |
| `trace/` | Records a `TraceEvent` per external call; `GET /api/trace?after=` serves them. |
| `db/` | SQLAlchemy tables, seed, repositories; mapped to `models.py` contracts. |
| `models.py` | API contracts (fixed; see `docs/contracts.md`). |
| `settings.py` | Env-only config; refuses a non-sandbox PayPal URL. |

## Key flows
1. **Benchmark:** intents (cached LLM) → Channel3 competitors (cached) → embed all (fastembed) → rank with constraint filters → metrics.
2. **Enrichment:** product text → LLM structured extraction (JSON schema + source spans) → grounding validator → diff → approval → DB + PayPal Catalog PATCH → benchmark re-run.
3. **Shopper:** request → ranker picks → LLM explanation → Orders v2 create → JS SDK approval → capture → webhook (or poll) → tag `source=agent`.

## Modes
- `APP_MODE=live`: real calls. Fixtures are reused when present (`cache_first`), `RECORD=1` refreshes them. Writes always go live.
- `APP_MODE=replay`: fixtures only; no keys needed; a missing fixture is an error, never a silent live call; "Replay" badge visible.

## Concurrency
Sync route handlers and sync `httpx.Client`; FastAPI runs them in its threadpool. The only async route is the PayPal webhook (it needs the raw body for signature verification). The API Trace panel polls about once a second, which is sturdier on Render's free tier than SSE or WebSockets.

## Tech choices
Backend: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0/SQLite, httpx, structlog, scikit-learn, fastembed, uv.
Frontend: React 19, Vite 8, TypeScript 5.9 (strict), TanStack Query, openapi-fetch + openapi-typescript, AG Grid, AG Studio, PayPal JS SDK v6, Playwright.
Deploy: Docker multi-stage build (node:22-slim → python:3.12-slim) on Render free tier. CI: GitHub Actions running `make check` plus a gitleaks scan.
