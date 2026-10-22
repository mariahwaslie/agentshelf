# Prompt 10 — Hardening, full review, final evaluation

| | |
|---|---|
| **Model** | Opus |
| **Time box** | 4–6 hours |
| **Serves judging criteria** | All five; especially Technological Implementation (tie-breaker) |
| **Read first** | `CLAUDE.md`, `docs/STANDARDS.md`, `docs/TESTING.md`, `docs/EVALUATION.md`, all reports in `docs/reports/` |
| **Depends on** | `prompt-09-done` |

## Objective
Find and fix everything a skeptical senior engineer or judge would catch, and finalize the evidence.

## Tasks
1. **Full-repo `/review`** (not just the last diff): correctness, security, standards, dead code, TODOs, honesty checks (no special-casing, no unlabeled cached results). Fix all High/Medium.
2. **Security pass:** secret scan of full history (`gitleaks detect`), webhook verification, input validation, sandbox guard, CORS, dependency audit (`pip-audit`, `npm audit` — fix High).
3. **Performance:** cold start, benchmark time, page load; fix anything that would make a judge wait > 5 s after warm-up.
4. **Finalize `docs/EVALUATION.md`:** results table, baseline comparison, pick-model metrics, feature-importance chart, limitations. Numbers must be reproducible by `make eval`.
5. **Code readability pass** on the files judges are most likely to open (`clients/paypal.py`, `domain/ranking.py`, `domain/enrichment.py`, `domain/shopper.py`, webhook handler): clear names, short functions, comments that explain *why*.
6. Run the **`judge` agent** on all five criteria using README, screenshots, and evaluation doc. Record scores and fix the cheapest high-value gaps.
7. **Demo lock prep:** record final replay fixtures for the demo (`make record`), review the diff, commit.

## Definition of Done
- [ ] Zero High/Medium review findings open
- [ ] No secrets in git history; dependency audit clean of High
- [ ] `make eval` reproduces `docs/EVALUATION.md` numbers
- [ ] Judge-agent scores recorded with what changed
- [ ] Golden, E2E, `make check` green on CI

## Verify / Review / Close
Report → `/end-session`.
