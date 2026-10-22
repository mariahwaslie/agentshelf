# Prompt 06 — Shopper agent + PayPal checkout loop

| | |
|---|---|
| **Model** | Opus |
| **Time box** | 6–9 hours across 1–2 sittings (checkpoint commit after order creation works) |
| **Serves judging criteria** | Technological Implementation (tie-breaker), Best Use of Agentic Commerce, Presentation (the wow moment) |
| **Read first** | `CLAUDE.md`, `SPEC.md` (F5), `DEMO_SCRIPT.md`, `docs/PROGRESS.md`, `docs/contracts.md`, `docs/reports/01-spikes.md` |
| **Depends on** | `prompt-05-done` |

## Objective
The wow moment works every time: same request, before vs. after — the agent now picks her product, creates a PayPal order, the buyer approves (PayPal + Pay Later visible), capture, webhook, and the sale is tagged agent-sourced.

## Mariah's task this session
Do one sandbox buyer approval yourself when asked (≈5 min) so you know how it looks for the video.

## Tests first
Webhook handler: signature verification (valid / invalid), idempotency (same event twice → one tag), out-of-order events, polling fallback reaching the same final state.

## Tasks
1. **Shopper agent** (`domain/shopper.py`): parse request → **reuse the benchmark ranker** to choose → LLM writes a short explanation citing the attributes that decided it. The LLM never chooses.
2. **Order creation:** via Agent Toolkit if the spike said go; else the REST client. Order includes the PayPal product reference and `custom_id` linking to the agent session.
3. **Buyer approval UI:** JS SDK v6 buttons with PayPal and **Pay Later** presented; clear "Agent proposed this — you approve" framing.
4. **Capture + webhook:** `/webhooks/paypal` verifies signature, processes each `event_id` once, tags the order `source=agent`; polling fallback if no webhook within N seconds.
5. **Shipment tracking** after capture (`FEATURE_SHIPMENT_TRACKING`) — only if time allows.
6. **Before/after split view:** run the golden query against the "before" snapshot and the current catalog side by side.
7. Agent-sourced revenue counter on the main page.

## Definition of Done
- [ ] Webhook tests (written first) pass
- [ ] Live run: golden query → her product → order → approval → capture → webhook verified → tagged. Record order ID, capture ID, webhook event ID
- [ ] Same flow passes in replay mode
- [ ] **Golden test fully green (no xfail)** — and stays green from now on
- [ ] Before/after split view screenshot matches `DEMO_SCRIPT.md` 1:30–2:15
- [ ] No hardcoded product choice anywhere (reviewer checks)

## Verify / Review / Close
`make check` + `make golden` → live evidence → `/review` (focus: payment correctness, idempotency, honesty of the pick) → report → `/end-session`.
