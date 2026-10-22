# Prompt 01 — Spikes: prove the risky parts early

| | |
|---|---|
| **Model** | Sonnet |
| **Time box** | 3–5 hours. **Each spike max 60 minutes**; if it exceeds that, stop that spike, record findings, choose the fallback. |
| **Serves judging criteria** | Technological Implementation (de-risking) |
| **Read first** | `CLAUDE.md`, `docs/PROGRESS.md`, `docs/RISKS.md`, `docs/contracts.md` |
| **Depends on** | `prompt-00-done` |

## Objective
Find out on day 2, not day 12, whether each risky integration works — and pick the fallback now if not.

## Rules for spikes
- Spike code lives in `spikes/` and is **throwaway**. It does not need tests or polish.
- Each spike produces a short write-up in the report: what worked, exact gotchas, code snippets worth keeping, and a go / fallback decision.
- Record real IDs and responses (redacted) as evidence.

## Step 0 — Plan (plan mode)
List the spikes, the success test for each, and your 60-minute stop point. Wait for approval.

## Spikes
1. **PayPal Orders v2 + JS SDK v6 + capture** in sandbox: create order server-side, approve in a minimal HTML page with PayPal **and Pay Later** buttons using the sandbox buyer, capture. Success = capture ID.
2. **PayPal webhooks:** register a webhook for `PAYMENT.CAPTURE.COMPLETED` pointing to a tunnel (cloudflared or ngrok), receive one event, call the **verify-webhook-signature** endpoint. Success = verified event. Also confirm the polling fallback (GET order) works.
3. **PayPal Catalog Products API:** create, GET, PATCH one product. Note which fields are supported.
4. **PayPal Agent Toolkit (Python) / MCP:** can the app create an order through the official Agent Toolkit in Python in 2026? Success = order created via toolkit. If not available or unstable → decision: REST client in-app, MCP at build time.
5. **Channel3 search:** one query for "waterproof hiking boots under $120"; inspect fields (price, availability, brand, attributes, offers). Note credit usage.
6. **Gemini free tier:** structured JSON output with a schema at temperature 0; measure latency and note rate limits observed.
7. **fastembed:** embed 500 short texts; measure **peak memory** and time. Success = peak RSS well under 400 MB for the whole Python process.
8. **AG Studio + Studio Agent Framework:** render a minimal dashboard in the React app **without a license key** (watermark OK). Try the PayPal + AG Studio boilerplate (github.com/paypaldev/hackathon-paypal-ag-grid-boilerplate) as a reference. Success = one widget renders from our data; note what the agent framework needs.

## Definition of Done
- [ ] Every spike has a go / fallback decision with evidence
- [ ] `docs/RISKS.md` updated (R1, R2, R4, R5, R6, R11 statuses)
- [ ] Any architecture change captured as a decision record
- [ ] Reusable snippets noted for prompt 02 (do not copy spike code wholesale into `backend/`)
- [ ] `make check` still green (spikes excluded from lint/tests)

## Verify / Review / Close
`/review` (focus: did each spike actually prove what it claims?) → report `docs/reports/01-spikes.md` → `/end-session`.
