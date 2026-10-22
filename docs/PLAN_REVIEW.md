# Plan Review Log

The starter kit went through four critique rounds before it was built. Each round reviewed the plan twice: once as a **senior developer** (will this code work, ship, and hold up?) and once as a **project manager** (will this finish on time, with the least of Mariah's time, and score well?). This log records what changed and why, so future sessions understand the reasoning behind the rules in `CLAUDE.md`.

---

## Round 1

### Senior developer findings
| # | Problem in the draft plan | Fix adopted |
|---|---|---|
| 1 | Two deployed services (API + frontend) on Render's free tier means two cold starts and CORS setup. | **Single service.** FastAPI serves the built React app. One Dockerfile, one URL. |
| 2 | `sentence-transformers` pulls in PyTorch. Render free tier has 512 MB RAM, so it would likely crash. | Use **fastembed** (ONNX, small). Memory under 512 MB is a spike check in prompt 01. |
| 3 | LLM output changes run to run, so the golden demo test would be flaky. | **Record/replay layer** for every external call (LLM, Channel3, PayPal). Tests and demo mode run on recorded fixtures; live mode is separate. LLM calls use temperature 0. |
| 4 | If an LLM decides which product the shopper agent buys, the "before/after flip" is not trustworthy. | The **ranker decides; the LLM only explains.** The shopper agent's pick comes from the same deterministic ranker the benchmark uses. |
| 5 | Webhooks need a public URL; local development has none. | Use a tunnel (cloudflared) during development, **plus an order-status polling fallback** so the demo never depends on webhook timing. |
| 6 | Free-tier LLM rate limits would choke a 200-query benchmark. | Generate intents and extract attributes once, cache to disk, reuse. Embeddings run locally. |
| 7 | 80% coverage and strict typing on *everything* would eat build hours. | Strict typing and 80% coverage apply to the **core package only** (benchmark, ranking, enrichment, webhooks, clients). UI gets one end-to-end smoke test. |

### Project manager findings
| # | Problem | Fix adopted |
|---|---|---|
| 1 | No single place telling Mariah what to do and when. | **`START_HERE.md`**: accounts, the session routine, the calendar, and her checklist. |
| 2 | Devpost submission left to the end. Devpost gets slammed near deadlines. | **Save a Devpost draft by Nov 5**, submit by **Nov 10**, two days of buffer. |
| 3 | Rules forbid third-party trademarks in the video without permission. Channel3 returns real brand names. | **Anonymized display mode** ("Competitor A/B/C") used for the video and screenshots. |
| 4 | No risk tracking. | **`docs/RISKS.md`** with owner, trigger, and fallback for each risk. |
| 5 | The project should help in interviews, but Mariah has little time to study the code. | Every Verification Report ends with a **"Explain it in 60 seconds"** section she can read in two minutes. |

---

## Round 2

### Senior developer findings
| # | Problem | Fix adopted |
|---|---|---|
| 1 | Python data models and TypeScript types can drift apart. | **TypeScript types are generated** from FastAPI's OpenAPI schema (`openapi-typescript`). A drift check runs in `make check`. |
| 2 | Judges reward "real API use", but nothing shows it on screen. | **API Trace panel**: a live side panel listing every PayPal/Channel3 call with real sandbox IDs. Doubles as video proof. |
| 3 | Enrichment could "win" by keyword-stuffing descriptions, which is dishonest and fragile. | **Grounding rule:** every extracted attribute must cite the source text it came from. Ungrounded suggestions are flagged, never auto-applied. Evaluation runs on a **held-out query set**. |
| 4 | PayPal access tokens expire (hours). | Token caching with automatic refresh inside the PayPal client. |
| 5 | The cut list existed only on paper. | **Feature flags** for each cuttable feature, so cutting is a config change, not a rewrite. |
| 6 | Database on Render's free tier resets on restart. | **Seed on boot** plus a **"Reset demo" button**, so a fresh state is always one click away. |

### Project manager findings
| # | Problem | Fix adopted |
|---|---|---|
| 1 | Deployment was scheduled late (prompt 09). Deploy problems found late are the classic hackathon killer. | **First deploy happens in prompt 02** (walking skeleton). Prompt 09 becomes judge-proofing only. |
| 2 | Sessions could run long and burn Max usage limits. | Each prompt has a **time box**, a **mid-session checkpoint commit**, a **30-minute stuck rule**, and a recommended model (Sonnet vs Opus). |

---

## Round 3

### Senior developer findings
| # | Problem | Fix adopted |
|---|---|---|
| 1 | The golden flip only works if the demo data makes it happen. Rigging it would be dishonest. | The hero product is **genuinely under-described** in the seed data, the ranker is fixed before enrichment runs, and **metrics are reported over the full held-out query set**, not just the hero query. The write-up says plainly that the hero query was chosen to illustrate. |
| 2 | One bad session could corrupt earlier work. | Every prompt ends with a **git tag** (`prompt-04-done`) so any session can be rolled back in one command. |
| 3 | Agent Toolkit availability for Python in 2026 was assumed, not verified. | Prompt 01 spike verifies it. Fallback: direct REST client (still full PayPal integration), with the PayPal MCP server used for build-time development. |

### Project manager findings
| # | Problem | Fix adopted |
|---|---|---|
| 1 | AG Studio trial lasts 45 days, but the spike (Oct 24) needs it and judging runs to Dec 15. | Spike runs **without a license key** (dev mode shows a watermark). Mariah starts the trial **Oct 31**, which covers through Dec 15. |
| 2 | If something goes badly wrong late, there is no video at all. | Record a **rough backup video on Nov 6**, then the polished one Nov 8–9. |

---

## Round 4

| Area | Finding | Result |
|---|---|---|
| Scope vs. time | 12 sessions, 40–55 hours, fits Oct 23 – Nov 9 with buffer. | No change. |
| Security | Claude Code settings now **deny reading `.env`**, so keys never enter a session transcript. | Added `.claude/settings.json`. |
| Judging | A second agent, **`judge`**, scores the project against the five official criteria in prompts 08 and 10, separate from the code reviewer. | Added `.claude/agents/judge.md`. |
| Anything else? | Remaining ideas (Storybook, load testing, i18n) cost more time than they return for a hackathon judged on a 3-minute video and a working demo. | **Stopped here.** Further changes would add process without adding score. |
