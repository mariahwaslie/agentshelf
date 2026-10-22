# Prompt 03 — Catalog and demo data, done properly

| | |
|---|---|
| **Model** | Sonnet |
| **Time box** | 3–5 hours |
| **Serves judging criteria** | Potential Impact (realism), Presentation (demo story) |
| **Read first** | `CLAUDE.md`, `SPEC.md` (F1), `DEMO_SCRIPT.md`, `docs/PROGRESS.md`, `docs/contracts.md` |
| **Depends on** | `prompt-02-done` |

## Objective
A realistic, honest demo catalog and query sets that make the story true, plus full catalog import and PayPal sync.

## Tasks
1. **Seed catalog** `data/catalog/seed.json`: ~40 products for *North Shore Trail Co.* (fictional Minnesota outdoor-gear shop): boots, jackets, packs, tents, base layers, accessories. Realistic prices.
   - Descriptions vary in quality the way real small shops do: some thorough, many **thin or inconsistent** (facts buried in prose, missing units, no fit info).
   - The **hero product** (wide-fit waterproof hiking boot, under $120) has the relevant facts present in its *notes or description text* but **not structured** — so grounded enrichment can honestly surface them. Do not make it artificially terrible.
   - Each product includes a `source_notes` field (what a merchant might have in a spreadsheet) that grounding can cite.
2. **Query sets:** generate shopper intents with the LLM (cached), dedupe, and split **train / held-out** (e.g., 70/30, stratified by category). Save to `data/queries/` with a version hash. Held-out is frozen from now on.
3. **Golden query:** confirm "waterproof wide-fit hiking boots under $120" (or propose a better one). **Ask Mariah to approve it.** Lock it in `DEMO_SCRIPT.md`.
4. **Record Channel3 fixtures** for all queries (watch credits; report usage).
5. **Import + sync:** CSV/JSON upload with validation and size limits; idempotent PayPal Catalog sync storing PayPal product IDs; "Reset demo" restores the seeded before-state.
6. Anonymized display mode for competitors (`DISPLAY_ANONYMIZED`).

## Definition of Done
- [ ] Seed catalog + query sets committed with version hashes; held-out frozen
- [ ] Golden query approved by Mariah and locked
- [ ] All ~40 products synced to PayPal sandbox (IDs stored); re-sync creates no duplicates (test)
- [ ] Channel3 fixtures recorded for every query; credits used reported
- [ ] Upload validation tests (bad rows, too large, wrong types)
- [ ] Reset demo works (test)
- [ ] Anonymized mode hides real brand names everywhere in the UI (test + screenshot)

## Verify / Review / Close
`make check` → evidence → `/review` (focus: is the seed data honest and realistic, not rigged?) → report → `/end-session`.
