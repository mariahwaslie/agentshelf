# Testing Plan

| Layer | Location | What it covers | Runs in |
|---|---|---|---|
| **Unit** | `backend/tests/unit/` | Ranking, metrics (recall@k, share of shelf), feature extraction, grounding validator, diff logic, webhook idempotency | `make check`, CI |
| **Contract** | `backend/tests/contract/` | Client modules against **recorded** PayPal / Channel3 / LLM responses (replay mode). No network, no credits. | `make check`, CI |
| **Integration** | `backend/tests/integration/` | Real sandbox: create product → create order → (manual or scripted approval) → capture → webhook received → tagged. Marked `@pytest.mark.live`, skipped unless `LIVE_TESTS=1` | Manually, before each checkpoint |
| **Golden demo test** | `backend/tests/golden/` | The full golden path in replay mode: before = competitor wins golden query; after enrichment approval = her product wins; order created; capture tagged `source=agent`; held-out share of shelf improves | `make golden`, `make check`, CI |
| **E2E smoke** | `frontend/e2e/` (Playwright) | Click through the golden path in the browser in replay mode | `make e2e` (prompts 08–10) |
| **Type drift** | `make check` | Regenerates TS types from OpenAPI and fails if they differ from committed | `make check`, CI |

## Coverage
- **≥ 80%** line coverage on `app/domain/`, `app/clients/`, `app/cache/`, and webhook handling.
- No coverage target for UI code beyond the E2E smoke test.

## Record/replay rules
- `APP_MODE=live` calls real services and **records** responses to `data/fixtures/` (secrets and auth headers stripped).
- `APP_MODE=replay` serves only recorded fixtures. A missing fixture is a test failure, not a silent live call.
- Fixtures are keyed by a hash of (service, method, path, normalized body).
- Re-record deliberately with `make record` and review the diff before committing.

## The golden demo test is sacred
- Written **failing** in prompt 00, made green progressively, must be green from prompt 06 onward.
- If it goes red: stop feature work and fix it first.
- It must not be "made green" by hardcoding the result. The reviewer agent checks for this.

## Live verification (each session that touches an integration)
Each Verification Report lists real sandbox IDs (product IDs, order IDs, capture IDs, webhook event IDs) observed during the session.
