# Risk Register

Update the **Status** column in `/end-session` when anything changes.

| # | Risk | Likelihood | Impact | Early warning | Mitigation / fallback | Status |
|---|---|---|---|---|---|---|
| R1 | PayPal sandbox checkout/webhook flow misbehaves | Medium | High | Prompt 01 spike fails | Polling fallback; tunnel for webhooks; PayPal Discord for help | Open |
| R2 | AG Studio harder to integrate than docs suggest | Medium | Medium | Prompt 01 spike > 90 min | Cut list #1–2: AG Grid Community + AG Charts | Open |
| R3 | AG Studio trial expires before judging ends | Low | Medium | — | Start trial Oct 31 (covers to Dec 15); replay mode screenshots | Open |
| R4 | Free LLM tier rate-limited or changed | Medium | Medium | 429s in spike | Cache everything; small batches; replay mode for demo | Open |
| R5 | Render free tier memory (512 MB) exceeded | Medium | High | Spike memory check | fastembed (ONNX); precompute catalog embeddings; lazy-load model | Open |
| R6 | Channel3 credits run out | Low | Medium | Credit counter in trace | Cache all responses; ask Channel3 on Discord for top-up | Open |
| R7 | Golden flip doesn't happen honestly with seed data | Medium | High | Prompt 04 numbers | Improve seed realism (thin descriptions on hero), revisit ranker features — never hardcode | Open |
| R8 | Max usage limits slow the build | Medium | Medium | Hitting limits twice in a week | Sonnet for routine prompts; tighter sessions; cut list | Open |
| R9 | Trademark issue in video (real competitor brands) | Medium | Medium | — | Anonymized display mode in video | Open |
| R10 | Judges can't run the app after deadline | Medium | High | — | Hosted URL + replay mode + `make demo` tested from fresh clone; README cold-start note | Open |
| R11 | Agent Toolkit (Python) unavailable or unstable | Medium | Low | Prompt 01 spike | Direct REST client; MCP used at build time | Open |
| R12 | Schedule slip | Medium | High | Missed checkpoint | Cut list applied after one-day slip | Open |
