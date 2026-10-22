# Coding Standards

These apply to every line of code. `make check` enforces most of them automatically; `/review` checks the rest.

## Python (backend)
- Python 3.12, managed with **uv**. Dependencies pinned in `pyproject.toml` + `uv.lock`.
- **ruff** for lint and format (line length 100). **mypy --strict** on `app/` core packages (`clients`, `domain`, `cache`, `trace`, `api`).
- **Type hints on every function.** No `Any` without a comment saying why.
- **Pydantic v2 models** for all request/response bodies, external API payloads, and config (`pydantic-settings`).
- No bare `except`. Catch specific exceptions; re-raise as domain errors with context.
- Functions do one thing; aim for < 40 lines. Modules < 400 lines.
- Docstrings on public functions: one line on *what* and *why*, not a restatement of the code.
- Logging via **structlog**, JSON in production, with `request_id`. **Never log secrets, tokens, or full payment payloads.**

## TypeScript (frontend)
- React + Vite + TypeScript **strict**. ESLint + Prettier.
- No `any`. API types are **generated** from the backend OpenAPI schema (`src/api/types.gen.ts`) — never hand-written.
- Components small and named for what they show (`VisibilityScoreCard`, not `Card2`).
- All API calls go through `src/api/client.ts`. Loading and error states for every fetch.
- Accessibility basics: labels on inputs, buttons are `<button>`, color is never the only signal.

## Architecture rules
- **Client modules are the only gateways** to external services: `clients/paypal.py`, `clients/channel3.py`, `clients/llm.py`, `clients/embeddings.py`.
- Every client call passes through the **record/replay cache** (`cache/`) and emits a **trace event** (`trace/`).
- Every external call has a **timeout**, **retry with exponential backoff** on 429/5xx (max 3), and a clear error.
- **Domain logic** (`domain/`) is pure where possible: no HTTP, no DB access inside scoring/ranking functions. Easy to unit test.
- Config only from environment via `settings.py`. Feature flags: `FEATURE_*` booleans.
- Determinism: fixed seeds (`SEED=42`), LLM temperature 0, data files versioned.

## Security
- Secrets only in `.env` (git-ignored). `.env.example` lists names with placeholder values.
- Pre-commit **secret scan** (gitleaks) blocks commits containing keys.
- PayPal webhooks: verify signature via PayPal's verify endpoint; reject unverified; process each `event_id` once.
- Validate and size-limit uploads (CSV/JSON ≤ 2 MB, ≤ 1,000 rows).
- Sandbox only. The app refuses to start if a PayPal base URL is not the sandbox URL.

## Git
- Conventional commits: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`.
- Small commits. Checkpoint commit mid-session. Each prompt ends with tag `prompt-NN-done`.
- Never commit `.env`, recorded fixtures containing secrets, or large binaries (> 5 MB).

## Definition of "good code" for this project
A judge opening any file should understand what it does in under a minute. Prefer clear names and small functions over clever code. Comments explain *why*, not *what*.
