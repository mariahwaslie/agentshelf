# AgentShelf — Project Brain

Read this file at the start of every session. It overrides your defaults.

## What we are building
**AgentShelf** is an agent-readiness copilot for small PayPal merchants. It measures whether AI shopping agents can find a merchant's products, fixes the gaps (with the merchant's approval), and proves the result with a real PayPal sandbox checkout made by an AI shopper agent.

Entry for the **PayPal AI Hackathon** (Devpost). Solo entrant: Mariah Waslie.
- **Hard deadline:** Thu Nov 12, 2026, 12:00 PM Pacific (2:00 PM Central).
- **Our submit target:** Tue Nov 10, 2026.

Full feature spec: `SPEC.md`. Demo storyline: `DEMO_SCRIPT.md`. Standards: `docs/STANDARDS.md`. Testing: `docs/TESTING.md`.

## How we win (keep this in mind for every decision)
Five judging criteria, **equally weighted**. Ties are broken by the first one.
1. **Technological Implementation** — thorough, skillful, non-trivial use of PayPal + AI. *(tie-breaker)*
2. **Design** — a complete, coherent product, not a tech demo.
3. **Potential Impact** — a credible, specific problem for a real audience, shown working.
4. **Innovation** — novel; differs from existing concepts.
5. **Presentation** — the video shows it working end to end and explains problem, audience, and why it matters.

Prize targets: **Best Use of Agentic Commerce** ($5k honorable mention) + one sponsor prize (**Channel3** $1.5k or **AG Grid** up to $5k). Grand prizes and Best Use of PayPal + AI are considered automatically.

Judging may include **automated AI review** that reads the README first. The README and repo must be clear on their own.

## The one thing that must always work: the golden path
Import catalog → run benchmark (low score, competitor wins) → enrichment proposes grounded fixes → merchant approves in grid → PayPal catalog updates → re-run benchmark (score rises) → shopper agent picks *her* product for the golden query → PayPal order → buyer approves (PayPal + Pay Later shown) → capture → webhook tags it agent-sourced → dashboard updates.

The golden demo test (`docs/TESTING.md`) guards this path. **If it is red, fixing it beats every other task.**

## Non-negotiable engineering rules
1. **The ranker decides, the LLM explains.** Product choice comes from the deterministic ranker. LLMs generate intents, extract attributes, and write explanations — never pick winners.
2. **Every external call goes through its client module** (`clients/paypal.py`, `clients/channel3.py`, `clients/llm.py`, `clients/embeddings.py`) and through the **record/replay cache**. Nothing else calls these services.
3. **Grounding.** Every attribute the enrichment agent proposes must cite the source text it came from. Ungrounded suggestions are flagged and never auto-applied.
4. **Human approval before any write** to PayPal or the catalog.
5. **Webhooks are signature-verified and idempotent** (keyed by event ID). Order-status polling is the fallback.
6. **Never read, print, log, or commit secrets.** Keys live only in `.env`. You are not permitted to open `.env`; use `.env.example` for names.
7. **Contracts are fixed.** Data models and routes in `docs/contracts.md` change only with a decision record in `docs/decisions/`.
8. **Synthetic, labeled data.** The demo store is fictional. Competitor data from Channel3 is real but shown **anonymized** in demo/video mode (trademark rule).
9. **Honest claims.** Metrics are reported over the held-out query set, with the method in `docs/EVALUATION.md`. Never present cached results as live without labeling them.

## Session rules
- Start every session with `/start-session`. End with `/end-session`.
- **Plan mode first.** Propose a plan; wait for approval before writing code.
- **Tests first** for core logic (ranking, scoring, enrichment grounding, webhook handling).
- **Stuck rule:** if one problem takes more than 30 minutes, stop, write what you tried in the report, and ask.
- **Ambiguity rule:** unclear + low impact → decide, note it in the report. Unclear + high impact (contracts, scope, anything user-visible in the demo) → ask.
- **Checkpoint commit** at the midpoint of long sessions.
- A session is done only when its Definition of Done passes, `make check` is green, `/review` findings are fixed, and the Verification Report is written.
- Stay inside the scope fence below. Ideas outside it go in `docs/PROGRESS.md` under "Parking lot", not into code.

## Scope fence (OUT of scope — do not build)
User accounts/login, multi-merchant support, real payments (sandbox only), mobile app, Bryntum, Shopify/WooCommerce integrations, real Store Sync/Agent Ready integration (not self-serve; we emulate the feed layer), i18n, dark-mode theming beyond what AG Grid gives for free, admin panels, email sending.

## Cut list (if behind schedule, cut in this order)
1. Studio custom agent (`FEATURE_STUDIO_AGENT`)
2. AG Studio dashboard → fall back to AG Grid Community + AG Charts (`FEATURE_AG_STUDIO`)
3. Shipment tracking after capture (`FEATURE_SHIPMENT_TRACKING`)
4. JSON-LD / agent feed export (`FEATURE_FEED_EXPORT`)
5. Learned pick-probability model → rule-based fix ranking (`FEATURE_PICK_MODEL`)

**Never cut:** the golden path, Channel3 benchmark, grounded enrichment + approval grid, PayPal checkout + webhook, API Trace panel, demo mode.

## Calendar and checkpoints
| Date | Prompt | Checkpoint |
|---|---|---|
| Oct 23 | 00 Kickoff | Architecture approved, contracts written, golden test exists (failing) |
| Oct 24 | 01 Spikes | All risky integrations proven or fallbacks chosen |
| Oct 25–26 | 02 Walking skeleton | **Hosted URL live** with a thin end-to-end path |
| Oct 27 | 03 Catalog + data | |
| Oct 28–29 | 04 Benchmark + ML | **Real before/after numbers** |
| Oct 30–31 | 05 Enrichment + grid | |
| Nov 1–2 | 06 Shopper + checkout | **Golden path works end to end** |
| Nov 3–4 | 07 Dashboard | |
| Nov 5 | 08 Design pass | **Devpost draft saved** |
| Nov 6 | 09 Judge-proofing | Rough backup video recorded |
| Nov 7 | 10 Hardening | Golden test green; evaluation report done |
| Nov 8 | 11 Submission package | **Demo locked** |
| Nov 8–9 | — | Mariah records final video |
| Nov 10 | — | **Submit** |

If a checkpoint slips by more than a day, apply the cut list before continuing.

## Repo map (target — confirmed in prompt 00)
```
backend/app/        FastAPI app: api/, clients/, domain/, cache/, trace/, models.py, settings.py
backend/tests/      unit/, contract/, integration/, golden/
frontend/src/       React + Vite + TS: pages/, components/, api/ (generated types), trace/
data/               seed catalog, query sets (train/held-out), recorded fixtures
docs/               standards, testing, evaluation, contracts, decisions, reports, progress
prompts/            one file per build session
```

## Commands
`make setup` · `make dev` · `make check` (lint + types + tests + type drift) · `make test` · `make golden` · `make e2e` · `make demo` (replay mode, no keys) · `make deploy-check`
