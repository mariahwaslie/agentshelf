# Prompt 05 — Grounded enrichment agent + AG Grid approval screen

| | |
|---|---|
| **Model** | Sonnet (switch to Opus for the grounding validator if it gets subtle) |
| **Time box** | 5–7 hours (checkpoint commit after the backend) |
| **Serves judging criteria** | Innovation (grounding), Design (approval UX), Technological Implementation, AG Grid sponsor prize |
| **Read first** | `CLAUDE.md`, `SPEC.md` (F4), `docs/PROGRESS.md`, `docs/contracts.md`, `docs/reports/04-benchmark-ml.md` |
| **Depends on** | `prompt-04-done` |

## Objective
The merchant sees exactly what to fix, why, and where each fact came from — approves it in a polished grid — and watches PayPal and the score update.

## Mariah's task this session
On **Oct 31**, start the AG Studio trial and paste the license key into `.env` (`AG_LICENSE_KEY`) and into Render's env vars. (Used fully in prompt 07; the grid here can use AG Grid Community or Enterprise.)

## Tests first
Grounding validator: given product text and a proposed attribute with a cited span, accept only if the span exists in the source and supports the value. Include adversarial cases (hallucinated "Gore-Tex", wrong unit, span from another product).

## Tasks
1. **Extraction** (`domain/enrichment.py`): LLM structured output (JSON schema) of attributes with `source_span` per attribute, from `description` + `source_notes`. Cached.
2. **Grounding validator:** exact/fuzzy span match + value-consistency rules. Ungrounded → status `needs_merchant_input`, never auto-applied.
3. **Rewrite proposals:** title/description rewrites using only grounded facts; diff against current.
4. **Fix prioritization:** order fixes by pick-model importance (or rule fallback) and show estimated impact.
5. **Approval grid (AG Grid):** one row per product; columns for current vs. proposed values; custom cell renderers for diffs (old struck through → new), a grounding-evidence tooltip, a visibility-impact badge; approve/reject per cell and per row; bulk approve; theming consistent with the app.
6. **Apply:** approved changes → DB → PayPal Catalog PATCH (verify by GET) → automatic benchmark re-run → new score shown with before/after delta. All writes visible in API Trace.
7. Fill in **after** numbers in `docs/EVALUATION.md` (held-out, plus baseline).

## Definition of Done
- [ ] Grounding tests (written first) pass, including adversarial cases
- [ ] No ungrounded attribute can reach PayPal (test)
- [ ] Approve → PayPal Catalog updated (GET confirms) → benchmark re-runs → score delta shown
- [ ] Held-out before/after metrics recorded; improvement is real on held-out, not only on the golden query
- [ ] Golden query "after": her hero product now ranks first (if not, diagnose honestly; do not special-case)
- [ ] Grid screenshots look professional at 1440×900; anonymized mode respected
- [ ] Golden test steps through "after benchmark" pass

## Verify / Review / Close
`make check` → evidence (PayPal product GET before/after) → `/review` (focus: can anything ungrounded leak through?) → report → `/end-session`.
