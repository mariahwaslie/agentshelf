# Prompt 08 — Design pass: one coherent, demo-ready product

| | |
|---|---|
| **Model** | Sonnet |
| **Time box** | 4–6 hours |
| **Serves judging criteria** | Design, Presentation, Best Demo Delivery |
| **Read first** | `CLAUDE.md`, `DEMO_SCRIPT.md`, `docs/PROGRESS.md`, all screenshots in `docs/reports/img/` |
| **Depends on** | `prompt-07-done` |

## Mariah's task today
Save a **Devpost draft** (title "AgentShelf" + tagline). Takes 5 minutes; it protects against last-day site problems.

## Objective
Make it feel like one product a merchant would trust, and make every scene in `DEMO_SCRIPT.md` look great on camera.

## Tasks
1. **Audit first:** screenshot every screen at 1440×900 and 1280×800. Run the **`judge` agent** on Design and Presentation using the screenshots. List problems before fixing.
2. One visual system: color tokens, type scale, spacing, consistent buttons/cards/empty states/loading/error states. Use the `frontend-design` skill if available.
3. Guided flow matching the demo: Import → Benchmark → Fix → Prove → Dashboard (stepper or clear nav).
4. Copy: plain language a shop owner understands; tooltips for metric terms.
5. API Trace panel: readable, collapsible, shows sandbox IDs prominently during checkout.
6. Accessibility basics: contrast, focus states, labels.
7. **Playwright E2E smoke test** of the golden path in replay mode (`make e2e`).

## Definition of Done
- [ ] Before/after screenshots of every screen in the report
- [ ] `judge` agent Design + Presentation scores improved; remaining issues listed
- [ ] Each `DEMO_SCRIPT.md` scene can be performed in order without workarounds
- [ ] E2E smoke test passes; golden test green; `make check` green
- [ ] Devpost draft saved (ask Mariah to confirm)

## Verify / Review / Close
`/review` → report → `/end-session`.
