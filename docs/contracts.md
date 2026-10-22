# Contracts

Data models and API routes. **Written in prompt 00 (2026-10-22).** After that, changes require a decision record in `docs/decisions/`.

- **Source of truth:** the `backend/app/models/` package (Pydantic v2; import from `app.models`) and the routers in `backend/app/api/`.
- **Frontend types** are generated from the OpenAPI schema into `frontend/src/api/types.gen.ts` (`make types`); `make check` fails if they drift.
- **Enforced by tests:** `backend/tests/contract/test_routes.py` fails if the app serves a route not listed here, misses one, or has a contract model no route exposes. `backend/tests/unit/test_models.py` covers the invariants below.
- **Database tables** (`backend/app/db/`, prompt 03) map to these models but are not part of the contract.

## Conventions
- All contract models reject unknown fields (`extra="forbid"`).
- **Money is integer cents** (`Money.amount_cents`) plus an ISO currency code. PayPal's decimal strings (`"119.00"`) are built only inside `clients/paypal.py`.
- Timestamps are ISO 8601 UTC.
- Enums are lowercase strings, except `OrderStatus` and `CaptureStatus`, which mirror PayPal's uppercase values.
- Attribute values are JSON-simple: `string | integer | boolean | string[]` (`AttributeValue`).
- Routes not built yet return **501** with `{"detail": "Not built yet (prompt NN)"}`.
- Every response, including a 500, carries an `X-Request-ID` header (the client's, if well-formed; else generated).
- OpenAPI `operationId` = the handler name (e.g. `get_product`).

## Invariants enforced by the models
These are validation rules, not conventions: a response that breaks one cannot be built.

| Rule | Where |
|---|---|
| **The ranker decides.** `pick` is exactly `ranked[0]` (or null when nothing ranked); ranks run 1..n; scores never increase. | `ShopperRecommendation`, `IntentResult` (`check_ranking`) |
| **Grounding.** `grounded=true` needs at least one `GroundingSpan`; a span's bounds match its text. | `EnrichmentProposal`, `GroundingSpan` |
| **Ungrounded never auto-applies.** An ungrounded proposal can be `approved` only with `merchant_supplied=true`. | `EnrichmentProposal` |
| **Agent revenue needs a real capture.** `capture_id` ⇔ `capture_status`, only on a `COMPLETED` order; `source` ⇔ `confirmed_by`; `source=agent` needs `capture_status=COMPLETED`; `confirmed_by=webhook` needs `webhook_event_id`. | `AgentOrder` |

## Data models

### Catalog
| Model | Fields | Notes |
|---|---|---|
| `Money` | `amount_cents: int ≥ 0`, `currency: str = "USD"` (3 uppercase letters) | |
| `ProductAttributes` | `material?`, `waterproof?: bool`, `waterproof_rating?`, `fit?`, `use_cases: str[]`, `sizes: str[]`, `colors: str[]`, `weight_grams?: int`, `gender?`, `season?`, `extra: {str: str}` | What agents filter on. PayPal Catalog can't hold these; the app DB does. |
| `Product` | `id`, `sku`, `title`, `description`, `notes = ""`, `category`, `price: Money`, `in_stock = true`, `image_url?`, `attributes`, `paypal_product_id?`, `updated_at` | `title`, `description`, `notes` are the only text enrichment may cite. |
| `Competitor` | `id`, `channel3_id` (opaque), `title`, `brand`, `description = ""`, `price: Money`, `in_stock = true`, `url?`, `attributes`, `anonymized: bool`, `fetched_at` | See **Anonymization** below. |
| `ImportResult` | `created`, `updated`, `product_ids: str[]` | |
| `SyncResult` | `created`, `updated`, `paypal_product_ids: {product_id: paypal_id}` | |

### Benchmark and diagnosis
| Model | Fields | Notes |
|---|---|---|
| `ShopperIntent` | `id`, `query`, `category`, `price_max?: Money`, `required_attributes: {str: AttributeValue}`, `split: train \| heldout` | Held-out intents never tune enrichment or ranking. |
| `RankedItem` | `rank ≥ 1`, `owner: merchant \| competitor`, `item_id`, `title`, `price`, `score` | Ranker output. |
| `CallProvenance` | `live_calls`, `reused_recordings`, `replayed_calls`, `oldest_recording_at?` | Where a result's external data came from (Channel3, LLM). The UI labels anything not fully live. |
| `BenchmarkRequest` | `split = heldout`, `k = 5` (1–20) | |
| `ProductScore` | `product_id`, `queries_considered`, `top_k_appearances`, `mean_rank?`, `top_competitor_id?` | |
| `BenchmarkRun` | `id`, `created_at`, `catalog_version`, `split`, `k`, `n_queries`, `mode`, `provenance: CallProvenance`, `visibility_score` (0–100), `share_of_shelf` (0–1), `recall_at_k` (0–1), `mean_best_rank?`, `baseline_share_of_shelf`, `baseline_recall_at_k`, `product_scores: ProductScore[]` | Metric definitions: `docs/EVALUATION.md`. `visibility_score` = share of shelf@k × 100. Baseline = keyword ranker on the same data. |
| `IntentResult` | `run_id`, `intent`, `ranked: RankedItem[]`, `competitors: Competitor[]` | One query's shelf (the before/after split view). |
| `Fix` | `product_id`, `kind: missing_attribute \| thin_description \| price_outlier \| availability`, `attribute?`, `message`, `estimated_impact: float`, `rank ≥ 1` | |

### Enrichment and approval
| Model | Fields | Notes |
|---|---|---|
| `GroundingSpan` | `source_field: title \| description \| notes`, `start ≥ 0`, `end`, `text` | Offsets count **Unicode code points** (Python indexing); the grid converts before slicing JS (UTF-16) strings. Enrichment also checks `text == product.<source_field>[start:end]`. |
| `EnrichmentProposal` | `id`, `product_id`, `field`, `old_value?`, `new_value: AttributeValue`, `spans: GroundingSpan[]`, `grounded: bool`, `merchant_supplied = false`, `status: pending \| approved \| rejected`, `rationale = ""` | `field` is an attribute name, `title`, or `description`. `grounded=false` shows as "needs merchant input". |
| `ProposalRequest` | `product_ids: str[]` (empty = all products) | |
| `ApprovalRequest` | `proposal_ids: str[]` (≥ 1), `decision: approve \| reject`, `merchant_values: {proposal_id: AttributeValue}` | `merchant_values` only with `approve`, only for IDs in the request. |
| `Approval` | `id`, `proposal_ids`, `decision`, `decided_at`, `paypal_synced_product_ids: str[]`, `benchmark_run_id?` | Approve writes DB + PayPal Catalog, then re-runs the benchmark. |

### Shopper agent and orders
| Model | Fields | Notes |
|---|---|---|
| `ShopperRequest` | `query` (3–300 chars) | |
| `ShopperRecommendation` | `id`, `query`, `intent: ShopperIntent`, `pick?: RankedItem`, `ranked: RankedItem[]`, `explanation`, `provenance: CallProvenance` | The LLM writes `explanation` and **never chooses** `pick` (enforced: `pick == ranked[0]`). |
| `CreateOrderRequest` | `recommendation_id` | |
| `AgentOrder` | `id`, `paypal_order_id`, `recommendation_id`, `product_id`, `query`, `amount: Money`, `status: CREATED \| SAVED \| APPROVED \| PAYER_ACTION_REQUIRED \| VOIDED \| COMPLETED`, `capture_id?`, `capture_status?: COMPLETED \| PENDING \| DECLINED \| FAILED \| REFUNDED \| PARTIALLY_REFUNDED`, `source?: agent`, `confirmed_by?: webhook \| polling`, `webhook_event_id?`, `created_at`, `captured_at?` | `source` is set only once the capture is confirmed COMPLETED, by the webhook or the polling fallback (`confirmed_by` says which). |
| `WebhookAck` | `event_id`, `processed: bool` | `processed=false` when the event ID was already handled. |

### Dashboard
| Model | Fields | Notes |
|---|---|---|
| `ScorePoint` | `run_id`, `created_at`, `visibility_score` | |
| `CategoryShare` | `category`, `share_of_shelf` (0–1) | |
| `DashboardSummary` | `visibility_history: ScorePoint[]`, `share_by_category: CategoryShare[]`, `agent_revenue: Money`, `other_revenue: Money`, `other_revenue_synthetic: bool`, `agent_order_count`, `most_invisible: ProductScore[]` | `agent_revenue` comes only from captured agent orders. `other_revenue` comes from the **seeded synthetic order history**; `other_revenue_synthetic=true` makes the UI label it. |

### System and feed
| Model | Fields | Notes |
|---|---|---|
| `HealthStatus` | `status: "ok"`, `mode: live \| replay`, `version`, `services: {paypal \| channel3 \| llm \| embeddings: configured \| missing_keys \| replay \| local}` | "configured" means keys are present; connectivity checks come with the clients. |
| `FeatureFlags` | `studio_agent`, `ag_studio`, `shipment_tracking`, `feed_export`, `pick_model` | Mirrors `FEATURE_*` env flags (the cut list). |
| `AppConfig` | `mode`, `display_anonymized`, `features`, `paypal_client_id?`, `ag_license_key?` | Both IDs are public by design: they ship to the browser on any PayPal JS SDK or AG Grid Enterprise page. The PayPal secret never leaves the server. |
| `ResetResult` | `products` | |
| `AgentFeed` | `generated_at`, `store_name`, `products: Product[]` | |
| `JsonLdDocument` | `{str: JSON}` | schema.org `Product` objects. |

## Anonymization (trademark rule)
When `DISPLAY_ANONYMIZED=true` (the default), **no real competitor brand reaches the browser**:
- It's a **server-side pass over every response that carries competitor data**: `Competitor` (brand → "Competitor A/B/C", brand scrubbed from `title`, `description` and `attributes`, `url` dropped), `RankedItem.title` for competitor items, `Fix.message`, and the LLM `explanation`.
- Text is anonymized **before** it goes into an LLM prompt, so the model never echoes a brand.
- Letters are stable within a benchmark run, so "Competitor A" means the same listing everywhere on a screen.
- `channel3_id` is treated as opaque and never derived from a brand.
- The golden test asserts that no brand string from the recorded Channel3 fixtures appears in any API response on the golden path.

## API routes
| Area | Route | Request | Response | Errors | Built in |
|---|---|---|---|---|---|
| System | `GET /health` | — | `HealthStatus` | | ✅ 00 |
| System | `GET /api/config` | — | `AppConfig` | | ✅ 00 |
| System | `POST /api/demo/reset` | — | `ResetResult` | | 03 |
| Trace | `GET /api/trace` | `?after=<seq>` (default 0) | `TraceEvent[]` with `seq > after` | | 02 |
| Catalog (F1) | `POST /api/catalog/import` | optional multipart `file` (CSV/JSON ≤ 2 MB, ≤ 1,000 rows); none = seed catalog | `ImportResult` | 413 too large, 422 bad rows | 03 |
| Catalog (F1) | `POST /api/catalog/sync` | — | `SyncResult` | | 03 |
| Catalog (F1) | `GET /api/products` | — | `Product[]` | | 03 |
| Catalog (F1) | `GET /api/products/{product_id}` | — | `Product` | 404 | 03 |
| Benchmark (F2) | `GET /api/intents` | `?split=train\|heldout` | `ShopperIntent[]` | | 03 |
| Benchmark (F2) | `POST /api/benchmark/runs` | `BenchmarkRequest` | `BenchmarkRun` (201) | | 04 |
| Benchmark (F2) | `GET /api/benchmark/runs` | — | `BenchmarkRun[]` | | 04 |
| Benchmark (F2) | `GET /api/benchmark/runs/{run_id}` | — | `BenchmarkRun` | 404 | 04 |
| Benchmark (F2) | `GET /api/benchmark/runs/{run_id}/intents/{intent_id}` | — | `IntentResult` | 404 | 04 |
| Diagnosis (F3) | `GET /api/fixes` | — | `Fix[]` (highest impact first) | | 04 |
| Diagnosis (F3) | `GET /api/products/{product_id}/fixes` | — | `Fix[]` | 404 | 04 |
| Enrichment (F4) | `POST /api/enrichment/proposals` | `ProposalRequest` | `EnrichmentProposal[]` | | 05 |
| Enrichment (F4) | `GET /api/enrichment/proposals` | `?status=pending\|approved\|rejected` | `EnrichmentProposal[]` | | 05 |
| Enrichment (F4) | `POST /api/enrichment/approvals` | `ApprovalRequest` | `Approval` | **422** if approving an ungrounded proposal without a `merchant_values` entry | 05 |
| Shopper (F5) | `POST /api/shopper/recommend` | `ShopperRequest` | `ShopperRecommendation` | | 06 |
| Shopper (F5) | `POST /api/orders` | `CreateOrderRequest` | `AgentOrder` (201) | 404 unknown recommendation; **409** if its pick is a competitor or null (the agent only buys the merchant's products) | 06 |
| Shopper (F5) | `GET /api/orders` | — | `AgentOrder[]` | | 06 |
| Shopper (F5) | `GET /api/orders/{order_id}` | — | `AgentOrder` (also polls PayPal live: the webhook fallback) | 404 | 06 |
| Shopper (F5) | `POST /api/orders/{order_id}/capture` | — | `AgentOrder` | 404; 409 if not buyer-approved | 06 |
| Webhooks | `POST /webhooks/paypal` | raw PayPal event bytes + `PAYPAL-TRANSMISSION-ID`, `-TRANSMISSION-TIME`, `-TRANSMISSION-SIG`, `-CERT-URL`, `-AUTH-ALGO` headers | `WebhookAck` | **400** if headers are missing or PayPal's verify-signature check fails; nothing changes | 06 |
| Dashboard (F6) | `GET /api/dashboard` | — | `DashboardSummary` | | 07 |
| Feed | `GET /api/feed/jsonld` | — | `JsonLdDocument[]` | | 07 |
| Feed | `GET /api/feed/agent.json` | — | `AgentFeed` | | 07 |

`/` and other extension-less paths serve the built React app (`frontend/dist`), with `index.html` as the fallback for client-side routes. Missing files (e.g. `/assets/x.js`) and unknown `/api/*`, `/webhooks/*`, `/health*` paths stay 404.

## Trace event schema
One `TraceEvent` per external call, recorded by the client layer and polled by the API Trace panel (about once a second).

| Field | Type | Meaning |
|---|---|---|
| `seq` | int ≥ 1 | Monotonic per process; the panel asks for `?after=<last seq>`. |
| `ts` | datetime | When the call started (UTC). |
| `service` | `paypal \| channel3 \| llm \| embeddings` | |
| `method` | str | HTTP method, or an operation name for non-HTTP clients (e.g. `embed`). |
| `endpoint` | str | **Templated** path, e.g. `/v2/checkout/orders/{id}/capture`. No query strings, so no keys. Real IDs go in `sandbox_ids`. |
| `status_code` | int? | HTTP status; null for non-HTTP calls or transport errors. |
| `duration_ms` | float ≥ 0 | Wall time, including replay lookup. |
| `cache` | `live \| recorded \| hit \| replayed \| miss` | `live` = called, not saved (credentials); `recorded` = called and saved; `hit` = live mode reused a recording; `replayed` = replay mode served a fixture; `miss` = replay had no fixture (an error). |
| `sandbox_ids` | `{str: str}` | Real sandbox IDs seen in the call, e.g. `{"product_id": …, "order_id": …, "capture_id": …}`. Video proof. |
| `error` | str? | Short error text; never a payload. |
| `request_id` | str? | The `X-Request-ID` of the API request that caused the call. |

**Never** in a trace event: auth headers, tokens, client secrets, API keys, full payment payloads.

## Record/replay
Defined in `backend/app/cache/` (the transport that uses it lands in prompt 02).

### Fixture keys (`keys.py`)
- **Key** = `sha256(canonical JSON of {service, operation, query, body})`, first 16 hex chars.
- **operation** = `"METHOD /path"` for HTTP, or a named operation for non-HTTP clients (`"embed:<model>"`).
- **query**: sorted pairs, repeated parameters kept; credential-bearing names (`key`, `api_key`, `apikey`, `access_token`, `client_secret`) are dropped.
- **body**: JSON compared by meaning (key order ignored); other bodies (e.g. OAuth form posts) as sorted form pairs with the same credential names dropped.
- **Volatile fields**: request bodies are built from seeded/deterministic values. A field that is unavoidably volatile (timestamp, generated `invoice_id`) is named in `ignore_fields` and removed at any depth before hashing.
- **Headers never take part** (auth and per-request IDs aren't meaning).
- **File**: `data/fixtures/<service>/<METHOD_path_slug>__<digest>.json`, human-readable for diff review.

### What happens to a call (`store.py`)
`cache_action(CacheMode, CallPolicy)`. The mode is app-wide (`cache_mode_for(APP_MODE, RECORD)`); the policy belongs to the operation.

| Policy → / Mode ↓ | `reusable` (Channel3 search, LLM at temp 0, embeddings) | `always_live` (**every PayPal call**) | `never_record` (PayPal OAuth token) |
|---|---|---|---|
| `replay` | serve fixture (missing = error) | serve fixture (missing = error) | stub: no call, placeholder token |
| `cache_first` (live) | reuse recording, else call + record | call + record | call only |
| `refresh` (live, `RECORD=1`) | call + record | call + record | call only |

PayPal is `always_live` so order status (the polling fallback), catalog GETs (proof of an update) and webhook verification always reflect current state outside replay.

### Redaction
A `Fixture` redacts on construction: credential fields in the body (`access_token`, `refresh_token`, `id_token`, `client_secret`, `api_key`, `nonce`) at any depth become `"[redacted]"`, and only allow-listed response headers (`content-type`) are kept. No fixture can hold a secret, whoever builds it.
