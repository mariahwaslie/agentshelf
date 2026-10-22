---
description: Start a build session — load context, check health, confirm the plan
---
Start a build session.

1. Read `CLAUDE.md`, then the **top entry** of `docs/PROGRESS.md`, then `docs/RISKS.md`.
2. Run `git status` and `git log --oneline -5`. If the working tree is dirty, stop and ask what to do.
3. Run `make check` and `make golden`. Report results in one line each. If the golden test was green last session and is red now, that is the first thing to fix.
4. Report today's date against the calendar in `CLAUDE.md`: are we on schedule? If a checkpoint slipped by more than a day, recommend which cut-list item to apply.
5. Summarize in 5 lines or fewer: last completed prompt, next prompt, open blockers, any risks that changed.
6. Then wait for the prompt to run (e.g., `Run @prompts/NN-name.md`). Stay in plan mode until the plan is approved.
