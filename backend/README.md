# backend/

FastAPI app (Python 3.12, uv). Start with `make dev` from the repo root; the app is built by `app.main:create_app`.

| Path | What it is |
|---|---|
| `app/models.py` | API contracts (fixed; documented in `docs/contracts.md`) |
| `app/settings.py` | Env-only config, feature flags, sandbox-only PayPal guard |
| `app/api/` | One router per product area |
| `app/domain/` | Pure logic: ranking, metrics, grounding (no HTTP, no DB) |
| `app/clients/` | The only gateways to PayPal, Channel3, the LLM and embeddings |
| `app/cache/` | Record/replay fixture keys and store interface |
| `app/trace/` | API Trace events |
| `app/db/` | SQLite via SQLAlchemy 2.0 |
| `tests/` | `unit/`, `contract/`, `integration/` (live, opt-in), `golden/` |

See `docs/ARCHITECTURE.md` and `docs/TESTING.md`.
