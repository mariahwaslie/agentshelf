# Progress Log

Updated by `/end-session`. Newest first. The next session reads the top entry first.

## Current status
- **Last completed prompt:** `prompts/00-kickoff.md` (tag `prompt-00-done`), finished Oct 22, one day ahead of the calendar
- **Next prompt:** `prompts/01-spikes.md` (calendar: Fri Oct 24)
- **Golden test:** exists, runs, **xfail** (fails for real at `POST /api/demo/reset → 501`); must be green from prompt 06
- **Open blockers:** none
- **Hosted URL:** not yet deployed (prompt 02)
- **Repo / CI:** https://github.com/mariahwaslie/agentshelf (public), CI green

## Session entries

### 2026-10-22 — Prompt 00: Kickoff ✅
- **Done:** Environment checked. Stack reviewed and accepted with amendments (`docs/decisions/0001-stack.md`): SQLAlchemy 2.0 instead of SQLModel, plain httpx for Gemini, TypeScript 5.9, ESLint, Node 24-era CI actions. Built the FastAPI backend (sandbox-only settings, request IDs, structured logs, 501 stubs for every contract route) and the Vite/React/TS frontend (generated API types, mode badge). Wrote `docs/contracts.md` in full, with invariants enforced by model validators, and the record/replay key scheme and per-call cache policy (`app/cache/`). Golden test written (xfail). Added the Dockerfile and `.dockerignore`; pre-commit with gitleaks is shown to block a fake key; `make keys-check` works; repo pushed and CI green.
- **Review:** 2 High + 11 Medium findings, all fixed; 17 Low, 13 fixed and 4 deferred with reasons (see `docs/reports/00-kickoff.md`).
- **Golden test:** xfail (expected).
- **Blockers:** none.
- **Hosted URL:** none yet.
- **Decisions for Mariah (non-blocking):**
  - Adopt `httpx2`? Starlette 1.9 prefers it over httpx and warns. Adding it was blocked pending vetting; we stay on httpx 0.28.1 for now.
- **Heads-up:** another local Docker container ("Loan Default Risk API") restarts with Docker Desktop and takes IPv6 port 8000. AgentShelf works alongside it (the Vite proxy uses `127.0.0.1`), but `curl localhost:8000` may hit the other app.
- **Deferred to later prompts:** stdlib/uvicorn logs through structlog (02); full-history gitleaks scan in CI and SHA-pinned actions (10); remove the `ARG001` ignore once the stubs are built (07); remove the golden xfail marker when it goes green (06).
- **Next:** `prompts/01-spikes.md`. Pick `LLM_MODEL` after checking current Gemini free-tier names; measure fastembed memory (image is 430 MB before it).

## Parking lot (ideas outside scope — do not build without approval)
-
