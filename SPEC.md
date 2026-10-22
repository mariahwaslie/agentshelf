# AgentShelf — Product Spec

## Problem
AI shopping agents are becoming a real sales channel, but they can only recommend products they can parse. PayPal's own merchant research found only about **1 in 5 merchants** have 80%+ of their catalog in structured, machine-readable form (23% among small businesses). PayPal's Store Sync distributes catalogs to AI channels, but a small merchant still can't answer two questions:
1. *Would an AI agent pick my product over a competitor's?*
2. *What exactly should I fix?*

AgentShelf answers both, then proves the fix with a real PayPal checkout started by an AI shopper.

Sources and exact figures: `docs/RESEARCH.md`. Verify every number there before it appears in the README or video.

## User
A small independent online merchant already on PayPal, 20–500 products, no data team.
**Demo persona:** *North Shore Trail Co.*, a fictional Minnesota outdoor-gear shop with ~40 products and inconsistent, thin descriptions.

## Features

### F1 — Catalog import and PayPal sync
- Load the seed catalog (`data/catalog/seed.json`) or upload CSV/JSON.
- Create/update products via **PayPal Catalog Products API** (`/v1/catalogs/products`). Store the PayPal product ID.
- Rich attributes (size, material, waterproof rating, fit, use case, etc.) live in the app database; PayPal Catalog holds product identity (it only supports thin fields).
- **Done when:** all seed products exist in PayPal sandbox with IDs stored, and re-import is idempotent.

### F2 — Agent Visibility benchmark (ML core)
- **Shopper intents:** an LLM generates realistic shopper queries per category, cached. Split into **train** and **held-out** sets (held-out is never used to tune enrichment).
- **Competitors:** for each intent, fetch comparable live listings from **Channel3** search (cached).
- **Ranker:** embeddings (fastembed) + attribute/constraint filters (price ceiling, required attributes) → ranked list mixing her products and competitors.
- **Metrics:** recall@k, share of shelf (fraction of top-k that are hers), mean rank per product. Also a **keyword baseline** for comparison.
- **Agent Visibility Score:** a 0–100 summary = share of shelf on the held-out set, documented in `docs/EVALUATION.md`.
- **Done when:** benchmark runs reproducibly (fixed seeds, versioned data) and reports per-product and store-level metrics.

### F3 — Gap diagnosis
- Per product: missing attributes vs. top competitors, price outliers, availability gaps.
- **Pick-probability model** (`FEATURE_PICK_MODEL`): logistic regression or gradient boosting on features (attribute completeness, price delta, availability, text match) predicting "lands in top-k". Feature importance tells the merchant which fixes matter most.
- **Done when:** each product has a ranked list of fixes with an estimated impact.

### F4 — Grounded enrichment agent + approval grid
- LLM extracts structured attributes from the product's own description/notes (JSON schema output). **Every attribute cites its source span.** Ungrounded suggestions are flagged "needs merchant input".
- Proposed rewrites of title/description use only grounded facts.
- **AG Grid** shows cell-level diffs (old → new), grounding evidence on hover, approve/reject per cell or row, bulk approve.
- Approved changes write to the app DB and PayPal Catalog, then the benchmark re-runs automatically.
- **Done when:** approve → PayPal catalog updated (verified by GET) → new score shown.

### F5 — Shopper agent + PayPal checkout (proof of purchase)
- A shopper agent takes a natural-language request, uses the **same ranker** to choose, and the LLM explains the choice.
- Creates a **PayPal Orders v2** order (via Agent Toolkit if the spike confirms it, else the REST client).
- Buyer approves with **JS SDK v6** buttons (PayPal + Pay Later shown). Agent proposes; human pays.
- Capture → **webhook** `PAYMENT.CAPTURE.COMPLETED` (signature-verified, idempotent) tags the order `source=agent`. Polling fallback.
- Optional (`FEATURE_SHIPMENT_TRACKING`): add tracking after capture.
- **Done when:** the golden query flips from competitor (before) to her product (after) and completes a sandbox capture recorded as agent-sourced revenue.

### F6 — Agent Channel dashboard
- **AG Studio** dashboard (`FEATURE_AG_STUDIO`): visibility score over time, share of shelf by category, agent-sourced vs. other revenue, top "invisible" products. Custom widgets and theming.
- **Studio custom agent** (`FEATURE_STUDIO_AGENT`): answers "Which 5 products are most invisible to agents and why?" by talking to Studio's built-in agents.
- Fallback: AG Grid Community + AG Charts.

### Cross-cutting
- **API Trace panel:** live list of every PayPal/Channel3/LLM call (method, endpoint, status, sandbox IDs, duration). Secrets redacted.
- **Demo mode:** `APP_MODE=replay` serves recorded fixtures, works with no keys, shows a visible "Replay" badge.
- **Anonymized display:** competitor brands shown as "Competitor A/B/C" when `DISPLAY_ANONYMIZED=true` (default in demo/video).
- **Reset demo** button restores the seeded "before" state.
- **Health page** `/health` shows which services are connected and the current mode.
- **Feed export** (`FEATURE_FEED_EXPORT`): schema.org Product JSON-LD and a simple agent-feed JSON file.

## Out of scope
See the scope fence in `CLAUDE.md`.

## Success criteria for submission
- Hosted URL works for judges through Dec 15, 2026 (live or replay).
- `make demo` runs from a fresh clone with no keys.
- Golden demo test green. Held-out metrics reported with a baseline.
- Video under 3:00 showing the before/after flip with real sandbox IDs on screen.
