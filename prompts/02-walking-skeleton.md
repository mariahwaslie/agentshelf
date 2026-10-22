# Prompt 02 — Walking skeleton + first deploy

| | |
|---|---|
| **Model** | Sonnet |
| **Time box** | 5–7 hours (checkpoint commit after the backend half) |
| **Serves judging criteria** | Technological Implementation, Design (end-to-end shape) |
| **Read first** | `CLAUDE.md`, `docs/PROGRESS.md`, `docs/contracts.md`, `docs/reports/01-spikes.md` |
| **Depends on** | `prompt-01-done` |

## Objective
A thin, ugly, **working** version of the entire golden path, deployed at a public URL. From today on, there is always something submittable.

## In scope
- **Real client modules** (`clients/paypal.py`, `channel3.py`, `llm.py`, `embeddings.py`) with timeouts, retries, token refresh (PayPal), and redaction — built from spike learnings, with contract tests on recorded fixtures.
- **Record/replay cache** fully implemented (`cache/`), plus `make record`.
- **Trace events** emitted by every client call; `/api/trace` endpoint; minimal API Trace panel in the UI.
- Thin version of each step: import 3 products → sync to PayPal → 3 hard-coded intents → Channel3 → naive ranking → show result → one fake "fix" → re-rank → create order → approve → capture → webhook/poll → tag.
- `APP_MODE=replay` works with no keys; "Replay" badge in the UI.
- **Deploy to Render** from GitHub via the Dockerfile. Walk Mariah through connecting Render and adding env vars (she pastes values; you never see them).

## Out of scope
Real ranking, real enrichment, styling, the full catalog.

## Step 0 — Plan (plan mode)
Show the order of work, which contract tests you'll write first, and the deploy steps Mariah must do. Wait for approval.

## Definition of Done
- [ ] Contract tests for all four clients pass in replay mode
- [ ] Cache: live mode records (secrets stripped — prove with a grep), replay mode never hits the network (prove with a test that blocks sockets)
- [ ] Thin golden path runs locally end to end in live mode once (IDs recorded) and in replay mode
- [ ] Golden test: steps that exist now pass; remaining steps still xfail
- [ ] API Trace panel lists real calls with sandbox IDs and no secrets
- [ ] **Hosted URL live**; `/health` OK; replay mode works on the hosted URL; cold start time noted
- [ ] Hosted memory usage noted (Render metrics) and under the limit

## Verify / Review / Close
`make check` → live run evidence → hosted URL screenshot → `/review` → report → `/end-session`. Put the hosted URL in `docs/PROGRESS.md`.
