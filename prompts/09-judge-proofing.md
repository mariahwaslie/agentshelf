# Prompt 09 — Judge-proofing: it must work for any judge until Dec 15

| | |
|---|---|
| **Model** | Sonnet |
| **Time box** | 3–5 hours |
| **Serves judging criteria** | Technological Implementation (functional demo requirement), Stage One pass/fail |
| **Read first** | `CLAUDE.md`, `SPEC.md` (cross-cutting), `docs/PROGRESS.md`, `docs/RISKS.md` (R3, R10) |
| **Depends on** | `prompt-08-done` |

## Mariah's task today
Record a rough **backup video** (phone or screen recording, follow `DEMO_SCRIPT.md`, ≤ 3 min). It is insurance; it does not need to be good.

## Objective
A judge with no keys, no context, and five minutes can see the full product working — through the hosted URL or a fresh clone — any day until judging ends Dec 15.

## Tasks
1. **Fresh-clone test:** clone the repo into a temp folder, follow only the README, run `make demo`. Fix every snag. Time it.
2. **Hosted demo hardening:** replay mode works with no keys; live mode degrades gracefully to replay if a key fails, with a visible notice; cold-start note on the landing page.
3. **Judge access:** sandbox buyer test credentials documented in README (sandbox only); a "Judge quick tour" button that walks the golden path.
4. **Health page** shows mode, each service status, data versions, build commit.
5. **Expiry audit:** list everything that could expire before Dec 15 (PayPal tokens, AG trial, Channel3 credits, LLM key, Render free tier sleep) and the fallback for each. Add to `docs/RISKS.md`.
6. Feed export (`FEATURE_FEED_EXPORT`) only if time allows.

## Definition of Done
- [ ] Fresh clone → `make demo` works by README alone (time recorded)
- [ ] Hosted URL works in replay with all keys removed (test on a preview env or by toggling)
- [ ] Graceful fallback demonstrated (screenshot)
- [ ] Expiry audit complete
- [ ] Backup video recorded (ask Mariah to confirm)
- [ ] Golden + E2E green; `make check` green

## Verify / Review / Close
`/review` → report → `/end-session`.
