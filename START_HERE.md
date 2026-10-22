# Start Here, Mariah

This kit lets Claude Code build AgentShelf in 12 sessions while you spend about **10–15 minutes per session** plus **~2 hours on the video**. Everything Claude needs is already written down; your job is to start sessions, approve plans, and glance at reports.

---

## Step 1 — Put the folder in place (2 min)
1. Unzip so the folder is at `~/Desktop/agentshelf`.
2. Open it in **Cursor**: File → Open Folder → Desktop → agentshelf.

## Step 2 — Accounts (about 1 hour total, all free)
Do the first five now. Keep keys in a note for the moment; prompt 00 shows you how to put them in `.env`.

| ✓ | Account | Where | What you need from it | When |
|---|---|---|---|---|
| ☐ | Devpost — join the hackathon | paypalaihackathon.devpost.com → **Join hackathon** | Registration | Now |
| ☐ | PayPal Developer | developer.paypal.com → Apps & Credentials → **Sandbox** → Create App | Client ID + Secret. Also note your **sandbox buyer** email/password (Testing Tools → Sandbox Accounts) | Now |
| ☐ | Channel3 | trychannel3.com/developers | API key. Apply promo code **PAYPAL-HACKATHON-2026** (20,000 free credits) | Now |
| ☐ | Google AI Studio (Gemini, free tier) | aistudio.google.com → Get API key | API key for the app's own AI calls | Now |
| ☐ | GitHub | github.com → New repository → `agentshelf`, **Public**, no README | Empty repo (first push happens after prompt 00) | Now |
| ☐ | Render | render.com → sign up with GitHub | Nothing yet; prompt 02 walks you through connecting | By Oct 25 |
| ☐ | **AG Studio trial** | ag-grid.com/studio/license-pricing | Trial license key | **On Oct 31 — not before** (the 45-day trial then lasts through judging on Dec 15) |

## Step 3 — The session routine (every session)
1. In Cursor, open Claude Code in the agentshelf folder.
2. Set the model the prompt recommends (`/model`). Sonnet for most; Opus for 00, 04, 06, 10.
3. Press **Shift+Tab** until it says **plan mode**.
4. Type: `/start-session` then `Run @prompts/NN-name.md` (NN = the prompt number).
5. **Read the plan** (2–3 min). If it looks reasonable, approve. If anything sounds off, ask "why?".
6. Let it work. Check back when it asks for approval or says it's done.
7. Read the **Verification Report** in `docs/reports/` — at least the summary and the "Explain it in 60 seconds" part (you'll use those in interviews).
8. It finishes with `/end-session`, which commits and tags the work.

**If a session gets stuck:** it will stop and write what it tried. Paste that into a chat with me and we'll sort it out.
**If something breaks badly:** `git reset --hard prompt-NN-done` returns to the last good session.

## Step 4 — Your calendar
| Date | Run | Your extra task |
|---|---|---|
| Thu Oct 23 | `00-kickoff` (Opus) | Accounts done; put keys in `.env` when it asks; first push to GitHub |
| Fri Oct 24 | `01-spikes` | — |
| Sat–Sun Oct 25–26 | `02-walking-skeleton` | Connect Render when it asks (~10 min) |
| Mon Oct 27 | `03-catalog-and-data` | Approve the golden query |
| Tue–Wed Oct 28–29 | `04-benchmark-ml` (Opus) | — |
| Thu–Fri Oct 30–31 | `05-enrichment-grid` | **Oct 31: start AG Studio trial**, give it the key |
| Sat–Sun Nov 1–2 | `06-shopper-checkout` (Opus) | Do one sandbox buyer approval yourself to see it works |
| Mon–Tue Nov 3–4 | `07-dashboard` | — |
| Wed Nov 5 | `08-design-pass` | **Save a Devpost draft** (title + one line is enough) |
| Thu Nov 6 | `09-judge-proofing` | Record a rough 3-min **backup video** (phone-quality is fine) |
| Fri Nov 7 | `10-hardening` (Opus) | — |
| Sat Nov 8 | `11-submission-package` | Read `docs/VIDEO_CHECKLIST.md` |
| Sat–Sun Nov 8–9 | — | **Record the final video** from `DEMO_SCRIPT.md` (1–2 hrs), upload to YouTube as **Public** |
| **Tue Nov 10** | — | **Submit on Devpost** (paste text from `docs/SUBMISSION.md`) |
| Nov 11–12 | — | Buffer. Deadline is **Nov 12, 2:00 PM your time**. |

## Stretching your Max usage
- Use the model each prompt recommends. Sonnet handles most sessions well.
- Run one session per sitting, not back-to-back marathons.
- If you hit a usage limit mid-session, it's fine: run `/end-session` when you're back and the next session picks up from `docs/PROGRESS.md`.

## What's in this folder
| File | What it's for |
|---|---|
| `CLAUDE.md` | The project brain Claude reads every session (rules, scope, calendar) |
| `SPEC.md` | What the product does |
| `DEMO_SCRIPT.md` | The 3-minute video plan |
| `prompts/` | One file per build session |
| `docs/` | Standards, testing plan, risks, research, evaluation, progress log, reports |
| `docs/PLAN_REVIEW.md` | How this plan was critiqued and improved before building |
| `.claude/` | Session commands (`/start-session`, `/verify`, `/review`…) and the reviewer + judge agents |
