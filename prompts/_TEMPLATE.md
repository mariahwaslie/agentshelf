# Prompt NN — Title

| | |
|---|---|
| **Model** | Sonnet / Opus |
| **Time box** | X–Y hours (checkpoint commit at the midpoint) |
| **Serves judging criteria** | … |
| **Read first** | `CLAUDE.md`, `docs/PROGRESS.md` (top entry), … |
| **Depends on** | prompt NN tagged done |

## Objective
One sentence.

## In scope
## Out of scope

## Interfaces you must honor
Contracts in `docs/contracts.md`. Do not change without a decision record.

## Step 0 — Plan (plan mode)
Propose a plan: files to create/change, tests to write first, risks, and how you'll verify. **Wait for approval.**

## Tasks

## Definition of Done
- [ ] …

## Verify
1. `make check` green.
2. Live verification as listed (record real IDs).
3. Screenshots of any UI touched (`docs/reports/img/NN-*.png`) — look at them.
4. Golden test status recorded.

## Review
Run `/review`. Fix every High and Medium finding. Re-run `make check`.

## Close
Write `docs/reports/NN-title.md` from the template, then run `/end-session`.
