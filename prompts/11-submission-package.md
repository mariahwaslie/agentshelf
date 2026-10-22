# Prompt 11 — Submission package + demo lock

| | |
|---|---|
| **Model** | Sonnet |
| **Time box** | 3–4 hours |
| **Serves judging criteria** | Presentation, Potential Impact, and the AI-assisted first-pass review |
| **Read first** | `CLAUDE.md`, `SPEC.md`, `DEMO_SCRIPT.md`, `docs/RESEARCH.md`, `docs/EVALUATION.md`, `docs/SUBMISSION.md`, `docs/VIDEO_CHECKLIST.md`, all reports |
| **Depends on** | `prompt-10-done` |

## Objective
Everything a judge reads or watches is clear, honest, and makes the strongest case — and the demo is frozen so nothing breaks before Dec 15.

## Tasks
1. **Verify every statistic** in `docs/RESEARCH.md` against its source (WebFetch). Update or drop anything that doesn't match. Mark verified.
2. **README** (for judges and automated review), in this order: one-line pitch + hosted URL + video link; the problem (2–3 verified stats); what it does (with 3 screenshots/GIF); how to try it in 2 minutes (hosted + `make demo` + sandbox buyer creds); architecture diagram; **every PayPal API/tool used and where in the code**; AI/ML components; evaluation results table; tests and quality (CI badge, coverage); limitations; AI tools disclosure; license.
3. **`docs/SUBMISSION.md`:** final Devpost text, each section mapped to a judging criterion. Concise. No hype words; concrete numbers.
4. **Video:** finalize the voiceover script in `DEMO_SCRIPT.md` with real numbers; produce a shot-by-shot checklist; check runtime by reading it aloud (< 2:50).
5. **Demo lock:** tag `demo-lock`; from now on only fixes for broken things, each with a test. Confirm the hosted service is deployed from the `demo-lock` commit.
6. **Repo hygiene:** license visible in GitHub About, description and topics set, no stray spike code in the main tree (move `spikes/` to `docs/spikes/` or delete), `.env.example` complete.
7. Final `judge` agent pass on README + SUBMISSION.md.

## Definition of Done
- [ ] All stats verified with links; nothing unverified in README/video/Devpost text
- [ ] README complete; renders correctly on GitHub
- [ ] SUBMISSION.md ready to paste
- [ ] Video script final with real numbers; under 2:50 read aloud
- [ ] `demo-lock` tag; hosted service on that commit
- [ ] Mariah has a clear checklist for recording and submitting (Nov 8–10)

## Verify / Review / Close
`/review` → report → `/end-session`. Tell Mariah: record the video Nov 8–9, submit Nov 10.
