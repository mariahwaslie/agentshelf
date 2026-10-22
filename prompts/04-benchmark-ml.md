# Prompt 04 — Agent Visibility benchmark + pick-probability model

| | |
|---|---|
| **Model** | Opus |
| **Time box** | 6–9 hours across 1–2 sittings (checkpoint commit after the ranker + metrics) |
| **Serves judging criteria** | Technological Implementation, Innovation, Potential Impact (evidence) |
| **Read first** | `CLAUDE.md`, `SPEC.md` (F2, F3), `docs/EVALUATION.md`, `docs/PROGRESS.md`, `docs/contracts.md` |
| **Depends on** | `prompt-03-done` |

## Objective
A reproducible, honest benchmark that measures how visible each product is to an AI shopping agent, plus a model that tells the merchant which fixes matter most. **This is Mariah's core data-science story — make it rigorous and explainable.**

## Tests first
Write unit tests for metric functions (share of shelf@k, recall@k, mean rank) with hand-computed examples, and for constraint filtering (price ceiling, required attributes), **before** implementing them.

## Tasks
1. **Ranker** (`domain/ranking.py`): fastembed embeddings of product text + structured attributes; query parsing into constraints (price ceiling, required attributes like waterproof/wide-fit) via cached LLM extraction; constraint filter + similarity score. Pure functions; deterministic.
   - The shopper agent (prompt 06) will reuse this exact ranker. Design for that.
2. **Keyword baseline** (BM25-style) for comparison.
3. **Benchmark runner** (`domain/benchmark.py`): runs train or held-out set, computes per-product and store-level metrics, stores a `BenchmarkRun`. Agent Visibility Score = share of shelf@5 on held-out × 100.
4. **Gap diagnosis** (`domain/diagnosis.py`): per product, missing attributes vs. top competitors, price outliers, availability.
5. **Pick-probability model** (`FEATURE_PICK_MODEL`, `domain/pick_model.py`): features (attribute completeness, price delta vs. competitor median, availability, text match score) → label "in top-5". Logistic regression first; try gradient boosting only if it clearly helps. **Grouped cross-validation by product** (no leakage). Report ROC AUC. Feature importance drives fix ranking. Rule-based fallback if the flag is off.
6. API routes + minimal UI: score card, per-product table, golden query result showing who wins.
7. Fill in `docs/EVALUATION.md` **Setup** and **before** numbers (after numbers come in prompt 05).

## Honesty checks (the reviewer will look for these)
- Held-out set never used to tune anything.
- Ranker frozen (config hash recorded) before enrichment.
- No code paths that special-case the hero product or golden query.

## Definition of Done
- [ ] Metric + filter unit tests (written first) pass; core coverage ≥ 80%
- [ ] Benchmark is reproducible: two runs → identical results (test)
- [ ] Before-numbers recorded in `docs/EVALUATION.md` with baseline comparison
- [ ] Golden query "before" result: a competitor wins (this is expected; if her product already wins, report it — **do not** degrade her data to force it)
- [ ] Pick model: grouped CV AUC reported; feature importance chart saved to `docs/reports/img/`
- [ ] Benchmark of the full held-out set runs in < 60 s in replay mode on the hosted service
- [ ] Golden test steps through "before benchmark" pass

## Verify / Review / Close
`make check` → `/review` (focus: leakage, determinism, special-casing) → report (include a plain-language explanation of the method) → `/end-session`.
