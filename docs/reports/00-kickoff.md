# Verification Report — Prompt 00: Kickoff

- **Date:** 2026-10-22 (one day ahead of the Oct 23 calendar slot)
- **Model used:** Claude Opus 5.5
- **Time spent (approx):** 1 hour wall-clock
- **Commit / tag:** `prompt-00-done` (set by `/end-session`; review fixes in `a5d31e3`)

## Summary (3 lines max)
AgentShelf is now an empty-but-correct project: FastAPI + React scaffold, every contract model and route written (routes answer 501 until built), and a golden test that fails for a real reason. Tooling is green locally and on GitHub CI, the Docker image builds and runs keyless in replay mode, and the pre-commit secret scan was shown to block a fake key. The independent review found 2 High and 11 Medium issues; all are fixed.

## Definition of Done
| Item | Status | Evidence |
|---|---|---|
| `make setup && make check` green on a clean checkout | ✅ | `make check` exit 0 locally (81 passed, coverage 99.24%, golden xfail, type drift ok); CI runs the same `make check` from a fresh checkout: runs 39855020874 and 39857813073 (review fixes, `a5d31e3`) green |
| `make dev` serves the placeholder page; `/health` returns `{"status":"ok","mode":...}` | ✅ | Vite :5173 returned the page; `/health` via the dev proxy returned `ok replay 0.1.0`; screenshot `docs/reports/img/00-placeholder.png` |
| `docker build` succeeds | ✅ | `make deploy-check` exit 0 (image 430 MB). Container smoke test: `/health` ok, SPA served, `/assets/missing.js` 404, `paypal_client_id` absent (no keys baked in), runs as non-root `app`, `backend/var` writable |
| `docs/contracts.md` complete; models compile; TS types generated | ✅ | `docs/contracts.md`; mypy strict clean on 34 files; `frontend/src/api/types.gen.ts` committed; `tests/contract/test_routes.py` ties code ↔ doc ↔ OpenAPI |
| Golden test exists, runs, and is xfail | ✅ | `make golden`: 1 xfailed. With `--runxfail` it fails at step 1: `POST /api/demo/reset → 501` |
| Pre-commit hooks installed; secret scan works | ✅ | A random fake `ghp_…` token in a temp file was blocked (`gitleaks … Failed`, `RuleID: github-pat`); HEAD unchanged; file deleted |
| `make keys-check` shows which keys are present | ✅ | PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, CHANNEL3_API_KEY, GEMINI_API_KEY present; PAYPAL_WEBHOOK_ID, LLM_MODEL, AG_LICENSE_KEY missing (all expected now) |
| Repo pushed; CI green on GitHub | ✅ | https://github.com/mariahwaslie/agentshelf (public). First run failed (`setup-uv@v10` tag doesn't exist), fixed by pinning `v10.3.2`; CI green since |

## Automated checks
- `make check`: ✅ ruff, ruff format, ESLint (strict type-checked), Prettier, mypy `--strict`, `tsc -b`, 81 unit + contract tests, golden (xfail), type drift
- Coverage on core: **99.24%** (`app/cache`, `app/api`, `app/trace`, `app/clients`, `app/domain`; only `api/deps.py`'s defensive branch uncovered)
- Golden test: xfail, as expected at this point in the calendar (must be green from prompt 06)
- Type-drift check proven: appending a line to `types.gen.ts` made `make types-check` fail with "stale: run 'make types'"

## Live verification (real sandbox / API evidence)
No PayPal, Channel3 or LLM calls this session (out of scope for prompt 00).

| What | ID / value |
|---|---|
| GitHub repo | `mariahwaslie/agentshelf` (public) |
| CI run (green, setup-uv fix) | 39855020874 |
| CI run (green, review fixes `a5d31e3`) | 39857813073 |
| Secret-scan block | gitleaks rule `github-pat` on a generated fake token |

## Screenshots
`docs/reports/img/00-placeholder.png`: the production build served by the Docker image at 1440×900. Checked: title, "Replay" badge, and the visible "No live calls are made" hint render correctly.

## Reviewer findings (`/review`)
| Finding | Severity | Fixed? |
|---|---|---|
| Golden webhook step posted re-serialized JSON with no PayPal signature headers, so it could only pass with verification bypassed | High | ✅ Posts recorded raw bytes + `PAYPAL-*` headers; unsigned and tampered deliveries must get 400 and leave the order untagged; 400 documented |
| Global `cache_first` in live mode: stale order status for polling, cached catalog GET as "proof", OAuth tokens written to git-tracked fixtures | High | ✅ Per-call `CallPolicy` (PayPal `always_live`, token `never_record`); `Fixture` redacts secrets on construction; tests |
| `ShopperRecommendation.pick` not tied to `ranked[0]` (rule 1) | Medium | ✅ Validator + ranking-shape check (`check_ranking`), tests |
| `grounded=True` allowed with no spans | Medium | ✅ Validator, test |
| No way to approve "needs merchant input" with a merchant value; ungrounded approval not refused | Medium | ✅ `ApprovalRequest.merchant_values`, `EnrichmentProposal.merchant_supplied`, validator, 422 documented |
| Anonymization only covered `Competitor` fields; brands could leak via ranked titles, LLM explanation, fixes | Medium | ✅ Contract defines a server-side pass over all competitor-bearing responses, anonymize-before-LLM; golden test asserts no recorded brand string appears in any response |
| Live mode could label reused recordings as live | Medium | ✅ `CallProvenance` on `BenchmarkRun` and `ShopperRecommendation`; trace `cache` adds `live`; badge reworded |
| `OrderStatus` missed `PAYER_ACTION_REQUIRED`/`SAVED`; no capture status | Medium | ✅ Full PayPal order and capture statuses; `capture_status` field |
| Volatile body fields would break replay keys | Medium | ✅ `ignore_fields` (any depth) + deterministic-bodies rule; test |
| A crashing handler returned a 500 without `X-Request-ID` and without a log line | Medium | ✅ Boundary catch logs `request_failed` and returns JSON 500 with the header; test |
| `AgentOrder` revenue invariants unenforced; test only checked defaults | Medium | ✅ Validator (capture ⇒ COMPLETED order, agent ⇒ COMPLETED capture, webhook ⇒ event ID); tests assert rejections |
| Golden test accepted self-reported PayPal IDs; no guard against a hardcoded golden query | Medium | ✅ Asserts PayPal PATCH/order/capture in the API Trace with matching `sandbox_ids`, `pick == ranked[0]`, same `k`/`n_queries`, and a paraphrased query flips too |
| Coverage gate left out webhook handling | Medium | ✅ Gate now covers `app/api` and `app/trace` |
| SPA fallback returned index.html for missing assets | Low | ✅ Only extension-less paths fall back; test |
| Non-root container user could not write anywhere (SQLite seed would fail) | Low | ✅ `backend/var` owned by `app`; `settings.var_dir`; verified in container |
| `get_logger` return type wrong; uvicorn/stdlib logs bypass structlog | Low | ◐ Type fixed. Routing stdlib logs through structlog **deferred to prompt 02** (deploy/logging work on Render) |
| `uv tool run pre-commit install` hook pointed into the uv cache | Low | ✅ `uv tool install pre-commit` first; hook now points at the persistent tool env |
| CI gitleaks scanned one commit; version differed from pre-commit | Low | ◐ `GITLEAKS_VERSION` aligned (8.30.0). Full-history CI scan **deferred to prompt 10**: the reviewer's local full-history scan was clean, and CI scans every pushed range from here on |
| No `permissions:` block; actions not SHA-pinned | Low | ◐ `permissions: contents: read` added. SHA pinning **deferred to prompt 10** (hardening) |
| HEAD not pushed before tagging; screenshot bundled into a frontend commit | Low | ✅ Pushed; CI checked on HEAD before tagging. The bundled commit is left as is (no history rewrite) |
| Async webhook handler would block the event loop on sync PayPal calls | Low | ✅ Sync handler + async `raw_body` dependency |
| `POST /api/orders` behavior undefined when the pick is a competitor or null | Low | ✅ 409 documented |
| AG license key unreachable by the browser | Low | ✅ `AppConfig.ag_license_key` (public by design) |
| `GroundingSpan` offsets ambiguous between Python and JS | Low | ✅ Documented as code points; grid converts |
| `other_revenue` source undefined | Low | ✅ Seeded synthetic history + `other_revenue_synthetic` flag for labeling |
| Repeated query params lost; form-body secrets hashed | Low | ✅ Sequence of pairs accepted; credential names dropped from form bodies; tests |
| `ARG001` ignored for all of `app/api/**` | Low | ⏭ **Deferred**: remove the ignore once the last stub is built (prompt 07) |
| `xfail(strict=False)` hides an XPASS | Low | ⏭ **Deferred to prompt 06**: remove the marker when the path goes green (the prompt requires `strict=False` now) |
| `make demo` printed its URL only after the server exited | Low | ✅ Printed before start |
| Replay disclaimer only in a tooltip | Low | ✅ Visible text + `aria-describedby` |

## Deviations from spec / decisions made
- **Stack amendments** (all in `docs/decisions/0001-stack.md`, now accepted): SQLAlchemy 2.0 instead of SQLModel; plain httpx for Gemini; TypeScript **5.9** (openapi-typescript doesn't support 6.0); ESLint instead of the template's oxlint; CI on Node 24-era action majors (Node 20 actions stopped working Sept 16, 2026).
- **`httpx2` not adopted.** Starlette 1.9's TestClient asks for `httpx2` (a successor to httpx published under the Pydantic GitHub org). Adding it was blocked by the session's safety check pending vetting, so the project stays on httpx 0.28.1 and the test config ignores that single deprecation warning. **Mariah's call** whether to adopt it later.
- **Money is integer cents**, not Decimal: exact, and generates clean TypeScript (`number`), where Decimal would come out as `number | string`.
- **`app/models.py` → `app/models/` package** to stay under the 400-line module limit; CLAUDE.md's repo map updated to the confirmed tree (adds `db/`, `models/`).
- **`.env` was not copied over** (it already existed). `make keys-check` confirmed the expected keys.
- **Uvicorn runs as a factory** (`--factory app.main:create_app`) so importing the app has no side effects.
- **Coverage gotcha:** `--cov=app.api.webhooks` (dotted module) broke route resolution under pytest's importlib mode; the directory form `--cov=app/api` works.
- **Transparency note:** a manual `curl /api/config` early in the session printed the **public** PayPal sandbox client ID (not the secret) into the session transcript. Later checks filter that field.

## Known issues and risks (also update docs/RISKS.md)
- **Port 8000 clash (local only):** another Docker container ("Loan Default Risk API") restarts with Docker Desktop and listens on IPv6 `*:8000`. The Vite proxy now targets `127.0.0.1` explicitly, so AgentShelf works alongside it; avoid `localhost:8000` in manual checks while it runs.
- **Image size 430 MB before fastembed/scikit-learn.** Relevant to R5 (512 MB RAM on Render): measure RAM in spike 01.
- Missing keys are all expected: `PAYPAL_WEBHOOK_ID` (prompt 02/06), `LLM_MODEL` (spike 01), `AG_LICENSE_KEY` (Oct 31).

## Next session should know
- Contracts are now fixed: changes need a decision record. The invariants table in `docs/contracts.md` is enforced by validators, so domain code must produce valid shapes (e.g. a recommendation's pick *is* `ranked[0]`).
- The record/replay transport (prompt 02) must follow the `cache_action(mode, policy)` table: every PayPal call is `always_live`; the OAuth token is `never_record` and stubbed in replay.
- The webhook fixture format the golden test expects: `data/fixtures/paypal/webhook_capture_completed.json` = `{"headers": {...PAYPAL-*...}, "body": "<raw JSON string>"}`, plus recorded verify-signature responses for both the real and the tampered body.
- The golden and paraphrase queries and `HERO_PRODUCT_ID` get locked in prompt 03.
- Spike 01: choose `LLM_MODEL` after checking current Gemini free-tier model names; measure fastembed memory.

## Explain it in 60 seconds (for Mariah's interviews)
Today I set up the skeleton of AgentShelf so every later piece has a fixed place to go. It's one service: a Python FastAPI backend that also serves the React app, packaged in a single Docker image. Before writing any features, I wrote the **contracts**: every data shape and API route the app will ever use. The frontend's TypeScript types are generated from them, so the two halves can't drift apart. I also wrote the **golden test** first. It describes the whole demo, from catalog import to an AI agent buying her product, and it fails today on purpose. A design choice worth mentioning: the project's honesty rules are written into the data models themselves. A recommendation is invalid unless the AI's pick is exactly the ranker's #1, and revenue can't be tagged "agent-sourced" until PayPal confirms the capture. So the rules can't be broken quietly. They fail loudly in tests.
