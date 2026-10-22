---
description: Run the full verification gate for the current prompt
---
Run the verification gate.

1. `make check` (lint, format check, types, unit + contract tests, coverage on core, type drift). Report pass/fail per step.
2. `make golden`. Report which steps pass and which are xfail (expected for this point in the calendar?).
3. If the frontend changed: `make e2e` (from prompt 08 on), and take screenshots of the touched screens at 1440×900 into `docs/reports/img/`. **Open and look at each screenshot**; note anything that looks broken.
4. If an integration changed and `LIVE_TESTS=1` is appropriate: run the live integration tests and record real sandbox IDs.
5. Walk the current prompt's **Definition of Done** item by item and mark each ✅/❌ with evidence.
6. Output a short table. Do not claim anything passed that you didn't run.
