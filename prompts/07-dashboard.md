# Prompt 07 — AG Studio "Agent Channel" dashboard + Studio agent

| | |
|---|---|
| **Model** | Sonnet |
| **Time box** | 4–6 hours. **If AG Studio fights you for > 90 min, apply cut list #1–2** (AG Grid Community + AG Charts) and move on. |
| **Serves judging criteria** | Design, AG Grid sponsor prize ("polish: custom widgets, theming, layout; Studio Agent Framework") |
| **Read first** | `CLAUDE.md`, `SPEC.md` (F6), `docs/PROGRESS.md`, `docs/reports/01-spikes.md` (AG Studio spike) |
| **Depends on** | `prompt-06-done`; `AG_LICENSE_KEY` present (`make keys-check`) |

## Objective
A polished dashboard that shows the merchant the "agent channel" at a glance, built the way AG Grid's judges asked for.

## Tasks
1. **AG Studio dashboard** (`FEATURE_AG_STUDIO`): Agent Visibility Score over time (each benchmark run), share of shelf by category, agent-sourced vs. other revenue, top 5 "invisible" products with their top fix.
2. **Custom widgets** (at least two) and a custom **theme** matching the app; sensible layout.
3. **Studio custom agent** (`FEATURE_STUDIO_AGENT`): answers "Which 5 products are most invisible to agents and why?" by talking to Studio's built-in agents and our data. Grounded in benchmark results; no invented numbers.
4. Data comes from our API only (no duplicated calculations in the frontend).

## Definition of Done
- [ ] Dashboard renders with real benchmark history and revenue data, live and replay
- [ ] ≥ 2 custom widgets + custom theme (screenshots)
- [ ] Studio agent answers the question correctly against the data (test with a known fixture), or cut is documented
- [ ] Golden test still green; `make check` green

## Verify / Review / Close
`/review` → report (note exactly which AG Studio features are used, for the Devpost write-up) → `/end-session`.
