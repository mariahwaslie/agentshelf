---
description: End a build session — verify, report, log progress, commit and tag
---
End the current build session.

1. Run `/verify`. If anything fails, fix it or record it as a known issue — do not hide it.
2. Make sure the Verification Report for this prompt exists in `docs/reports/` (from `docs/reports/TEMPLATE.md`), with every section filled, including **"Explain it in 60 seconds"**.
3. Update `docs/PROGRESS.md`: "Current status" block, plus a new session entry at the top (date, prompt, what was done, golden test status, blockers, hosted URL, next prompt).
4. Update status columns in `docs/RISKS.md` if anything changed.
5. Commit with a conventional message. If the prompt's Definition of Done is fully met, tag `prompt-NN-done`. If not, do **not** tag; explain what remains in PROGRESS.md.
6. Push (branch and tags).
7. Tell Mariah in 3–5 short lines: what got built, whether it passed, and what she needs to do before the next session (if anything).
