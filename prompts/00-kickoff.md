# Prompt 00 — Kickoff: setup, architecture, contracts, guardrails

| | |
|---|---|
| **Model** | Opus |
| **Time box** | 3–5 hours |
| **Serves judging criteria** | Technological Implementation (foundation), all others indirectly |
| **Read first** | `CLAUDE.md`, `SPEC.md`, `DEMO_SCRIPT.md`, `docs/STANDARDS.md`, `docs/TESTING.md`, `docs/ARCHITECTURE.md`, `docs/decisions/0001-stack.md`, `docs/PLAN_REVIEW.md` |
| **Depends on** | nothing |

## Objective
Turn this kit into a working, empty-but-correct project: tooling green, architecture confirmed, contracts written, golden test written (failing), and the repo pushed to GitHub.

## In scope
Environment check, scaffold, tooling, contracts, golden test skeleton, `.env` setup with Mariah, first push.

## Out of scope
Any feature logic. Any external API calls beyond a trivial "keys load" check.

## Step 0 — Plan (plan mode)
1. **Environment check** (read-only): report versions of Python, uv, Node, npm, git, Docker (optional), and whether the **PayPal AI Toolkit plugin** for Claude Code is installed (`/plugin install paypal@claude-plugins-official`). List anything missing with the exact install command for macOS. Do not install without approval.
2. Review `docs/ARCHITECTURE.md` and `docs/decisions/0001-stack.md` as a skeptical senior engineer. Propose any changes **with reasons**. For each major choice (web framework, ORM, embeddings library, LLM SDK, frontend build, test runner), give 2 options with trade-offs and a recommendation.
3. Propose the exact directory tree and the list of files you will create.
Wait for approval.

## Tasks (after approval)
1. Install missing tools Mariah approved.
2. **Backend scaffold** (`backend/`): uv project, FastAPI app with `/health`, `settings.py` (pydantic-settings; all `FEATURE_*` flags, `APP_MODE`, `DISPLAY_ANONYMIZED`, `SEED`), structlog setup with request IDs, empty packages `api/ clients/ domain/ cache/ trace/`, sandbox-only guard on PayPal base URL.
3. **Frontend scaffold** (`frontend/`): Vite + React + TS strict, ESLint, Prettier, `src/api/client.ts`, a placeholder page, and the `openapi-typescript` generation script.
4. FastAPI serves `frontend/dist` at `/` in production. **Dockerfile** (multi-stage: build frontend → slim Python runtime).
5. Make the provided `Makefile`, `.pre-commit-config.yaml`, and `.github/workflows/ci.yml` actually work with this scaffold (adjust if your plan changed paths). Install pre-commit hooks.
6. **Write `docs/contracts.md`**: Pydantic models and routes for everything in `SPEC.md` (Product, ProductAttributes, Competitor, ShopperIntent, BenchmarkRun, ProductScore, Fix, EnrichmentProposal with GroundingSpan, Approval, AgentOrder, TraceEvent) and every API route the frontend will need. Implement the models as code in `backend/app/models.py`; routes may return `501 Not Implemented` for now.
7. **Record/replay cache interface** (`cache/`): define the interface and fixture key scheme only (implementation in prompt 02).
8. **Golden test skeleton** (`backend/tests/golden/test_golden_path.py`): written against the contracts, describing every step of the golden path in `CLAUDE.md`. Marked `xfail(strict=False)` with reason "not built yet". It must fail for real reasons, not be empty.
9. **`.env`**: copy `.env.example` to `.env`. **Ask Mariah to paste her keys into `.env` herself** (do not read the file; you are denied access). Add a `make keys-check` target that reports which keys are *present* (never their values).
10. Update `docs/decisions/0001-stack.md` to **accepted** (or write new decision records for changes).
11. Initialize git, first commit, add the GitHub remote Mariah created, push. Confirm CI runs.

## Definition of Done
- [ ] `make setup && make check` green on a clean checkout
- [ ] `make dev` serves the placeholder page and `/health` returns `{"status":"ok","mode":...}`
- [ ] `docker build` succeeds (if Docker is installed; else note it for prompt 02)
- [ ] `docs/contracts.md` complete; models compile; TS types generated
- [ ] Golden test exists, runs, and is xfail
- [ ] Pre-commit hooks installed; secret scan works (prove it with a fake key in a temp file that gets blocked, then delete)
- [ ] `make keys-check` shows which keys are present
- [ ] Repo pushed; CI green on GitHub

## Verify / Review / Close
`make check` → `/review` → fix findings → report `docs/reports/00-kickoff.md` → `/end-session` (tags `prompt-00-done`).
