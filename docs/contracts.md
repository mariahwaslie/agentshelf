# Contracts

Data models and API routes. **Written in prompt 00 (2026-10-22).** After that, changes require a decision record in `docs/decisions/`.

- **Source of truth:** `backend/app/models.py` (Pydantic v2) and the routers in `backend/app/api/`.
- **Frontend types** are generated from the OpenAPI schema into `frontend/src/api/types.gen.ts` (`make types`); `make check` fails if they drift.
- **Enforced by tests:** `backend/tests/contract/test_routes.py` fails if the app serves a route not listed here, misses one, or has a contract model no route exposes.
- **Database tables** (`backend/app/db/`, prompt 03) map to these models but are not part of the contract.

## Conventions
- All contract models reject unknown fields (`extra="forbid"`).
- **Money is integer cents** (`Money.amount_cents`) plus an ISO currency code. PayPal's decimal strings (`"119.00"`) are built only inside `clients/paypal.py`.
- Timestamps are ISO 8601 UTC.
- Enums are lowercase strings, except `OrderStatus`, which mirrors PayPal's uppercase values.
- Attribute values are JSON-simple: `string | integer | boolean | string[]` (`AttributeValue`).
- Routes not built yet return **501** with `{"detail": "Not built yet (prompt NN)"}`.
- Every response carries an `X-Request-ID` header (the client's, if well-formed; else generated).
- OpenAPI `operationId` = the handler name (e.g. `get_product`).

## Data models

### Catalog
| Model | Fields | Notes |
|---|---|---|
| `Money` | `amount_cents: int ≥ 0`, `currency: str = "USD"` (3 uppercase letters) | |
| `ProductAttributes` | `material?`, `waterproof?: bool`, `waterproof_rating?`, `fit?`, `use_cases: str[]`, `sizes: str[]`, `colors: str[]`, `weight_grams?: int`, `gender?`, `season?`, `extra: {str: str}` | What agents filter on. PayPal Catalog can't hold these; the app DB does. |
| `Product` | `id`, `sku`, `title`, `description`, `notes = ""`, `category`, `price: Money`, `in_stock = true`, `image_url?`, `attributes`, `paypal_product_id?`, `updated_at` | `title`, `description`, `notes` are the only text enrichment may cite. |
| `Competitor` | `id`, `channel3_id`, `title`, `brand`, `description = ""`, `price: Money`, `in_stock = true`, `url?`, `attributes`, `anonymized: bool`, `fetched_at` | When `DISPLAY_ANONYMIZED=true` the **server** sets `brand` to "Competitor A/B/C", scrubs it from `title`, drops `url`. Real brands never reach the browser. |
| `ImportResult` | `created`, `updated`, `product_ids: str[]` | |
| `SyncResult` | `created`, `updated`, `paypal_product_ids: {product_id: paypal_id}` | |

### Benchmark and diagnosis
| Model | Fields | Notes |
|---|---|---|
| `ShopperIntent` | `id`, `query`, `category`, `price_max?: Money`, `required_attributes: {str: AttributeValue}`, `split: train \| heldout` | Held-out intents never tune enrichment or ranking. |
| `RankedItem` | `rank ≥ 1`, `owner: merchant \| competitor`, `item_id`, `title`, `price`, `score` | Ranker output. |
| `BenchmarkRequest` | `split = heldout`, `k = 5` (1–20) | |
| `ProductScore` | `product_id`, `queries_considered`, `top_k_appearances`, `mean_rank?`, `top_competitor_id?` | |
| `BenchmarkRun` | `id`, `created_at`, `catalog_version`, `split`, `k`, `n_queries`, `mode`, `visibility_score` (0–100), `share_of_shelf` (0–1), `recall_at_k` (0–1), `mean_best_rank?`, `baseline_share_of_shelf`, `baseline_recall_at_k`, `product_scores: ProductScore[]` | Metric definitions: `docs/EVALUATION.md`. `visibility_score` = share of shelf@k × 100. Baseline = keyword ranker on the same data. |
| `IntentResult` | `run_id`, `intent`, `ranked: RankedItem[]`, `competitors: Competitor[]` | One query's shelf (the before/after split view). |
| `Fix` | `product_id`, `kind: missing_attribute \| thin_description \| price_outlier \| availability`, `attribute?`, `message`, `estimated_impact: float`, `rank ≥ 1` | |

### Enrichment and approval
| Model | Fields | Notes |
|---|---|---|
| `GroundingSpan` | `source_field: title \| description \| notes`, `start ≥ 0`, `end`, `text` | Validated: `end > start` and `end − start == len(text)`. Enrichment also checks `text == product.<source_field>[start:end]`. |
| `EnrichmentProposal` | `id`, `product_id`, `field`, `old_value?`, `new_value: AttributeValue`, `spans: GroundingSpan[]`, `grounded: bool`, `status: pending \| approved \| rejected`, `rationale = ""` | `field` is an attribute name, `title`, or `description`. `grounded=false` shows as "needs merchant input" and is never auto-applied. |
| `ProposalRequest` | `product_ids: str[]` (empty = all products) | |
| `ApprovalRequest` | `proposal_ids: str[]` (≥ 1), `decision: approve \| reject` | |
| `Approval` | `id`, `proposal_ids`, `decision`, `decided_at`, `paypal_synced_product_ids: str[]`, `benchmark_run_id?` | Approve writes DB + PayPal Catalog, then re-runs the benchmark. |

### Shopper agent and orders
| Model | Fields | Notes |
|---|---|---|
| `ShopperRequest` | `query` (3–300 chars) | |
| `ShopperRecommendation` | `id`, `query`, `intent: ShopperIntent`, `pick?: RankedItem`, `ranked: RankedItem[]`, `explanation` | `pick` is the ranker's #1. The LLM writes `explanation` and **never chooses** `pick`. |
| `CreateOrderRequest` | `recommendation_id` | |
| `AgentOrder` | `id`, `paypal_order_id`, `recommendation_id`, `product_id`, `query`, `amount: Money`, `status: CREATED \| APPROVED \| COMPLETED \| VOIDED`, `capture_id?`, `source?: agent`, `confirmed_by?: webhook \| polling`, `webhook_event_id?`, `created_at`, `captured_at?` | `source` is set only once capture is confirmed, by the webhook or the polling fallback (`confirmed_by` says which). |
| `WebhookAck` | `event_id`, `processed: bool` | `processed=false` when the event ID was already handled. |

### Dashboard
| Model | Fields |
|---|---|
| `ScorePoint` | `run_id`, `created_at`, `visibility_score` |
| `CategoryShare` | `category`, `share_of_shelf` (0–1) |
| `DashboardSummary` | `visibility_history: ScorePoint[]`, `share_by_category: CategoryShare[]`, `agent_revenue: Money`, `other_revenue: Money`, `agent_order_count`, `most_invisible: ProductScore[]` |

### System and feed
| Model | Fields | Notes |
|---|---|---|
| `HealthStatus` | `status: "ok"`, `mode: live \| replay`, `version`, `services: {paypal \| channel3 \| llm \| embeddings: configured \| missing_keys \| replay \| local}` | "configured" means keys are present; connectivity checks come with the clients. |
| `FeatureFlags` | `studio_agent`, `ag_studio`, `shipment_tracking`, `feed_export`, `pick_model` | Mirrors `FEATURE_*` env flags (the cut list). |
| `AppConfig` | `mode`, `display_anonymized`, `features`, `paypal_client_id?` | The PayPal client ID is public by design (JS SDK). The secret never leaves the server. |
| `ResetResult` | `products` | |
| `AgentFeed` | `generated_at`, `store_name`, `products: Product[]` | |
| `JsonLdDocument` | `{str: JSON}` | schema.org `Product` objects. |

## API routes
| Area | Route | Request | Response | Built in |
|---|---|---|---|---|
| System | `GET /health` | — | `HealthStatus` | ✅ 00 |
| System | `GET /api/config` | — | `AppConfig` | ✅ 00 |
| System | `POST /api/demo/reset` | — | `ResetResult` | 03 |
| Trace | `GET /api/trace` | `?after=<seq>` (default 0) | `TraceEvent[]` with `seq > after` | 02 |
| Catalog (F1) | `POST /api/catalog/import` | optional multipart `file` (CSV/JSON ≤ 2 MB, ≤ 1,000 rows); none = seed catalog | `ImportResult` | 03 |
| Catalog (F1) | `POST /api/catalog/sync` | — | `SyncResult` | 03 |
| Catalog (F1) | `GET /api/products` | — | `Product[]` | 03 |
| Catalog (F1) | `GET /api/products/{product_id}` | — | `Product` | 03 |
| Benchmark (F2) | `GET /api/intents` | `?split=train\|heldout` | `ShopperIntent[]` | 03 |
| Benchmark (F2) | `POST /api/benchmark/runs` | `BenchmarkRequest` | `BenchmarkRun` (201) | 04 |
| Benchmark (F2) | `GET /api/benchmark/runs` | — | `BenchmarkRun[]` | 04 |
| Benchmark (F2) | `GET /api/benchmark/runs/{run_id}` | — | `BenchmarkRun` | 04 |
| Benchmark (F2) | `GET /api/benchmark/runs/{run_id}/intents/{intent_id}` | — | `IntentResult` | 04 |
| Diagnosis (F3) | `GET /api/fixes` | — | `Fix[]` (highest impact first) | 04 |
| Diagnosis (F3) | `GET /api/products/{product_id}/fixes` | — | `Fix[]` | 04 |
| Enrichment (F4) | `POST /api/enrichment/proposals` | `ProposalRequest` | `EnrichmentProposal[]` | 05 |
| Enrichment (F4) | `GET /api/enrichment/proposals` | `?status=pending\|approved\|rejected` | `EnrichmentProposal[]` | 05 |
| Enrichment (F4) | `POST /api/enrichment/approvals` | `ApprovalRequest` | `Approval` | 05 |
| Shopper (F5) | `POST /api/shopper/recommend` | `ShopperRequest` | `ShopperRecommendation` | 06 |
| Shopper (F5) | `POST /api/orders` | `CreateOrderRequest` | `AgentOrder` (201) | 06 |
| Shopper (F5) | `GET /api/orders` | — | `AgentOrder[]` | 06 |
| Shopper (F5) | `GET /api/orders/{order_id}` | — | `AgentOrder` (also polls PayPal: the webhook fallback) | 06 |
| Shopper (F5) | `POST /api/orders/{order_id}/capture` | — | `AgentOrder` | 06 |
| Webhooks | `POST /webhooks/paypal` | raw PayPal event JSON + `PAYPAL-*` signature headers | `WebhookAck` | 06 |
| Dashboard (F6) | `GET /api/dashboard` | — | `DashboardSummary` | 07 |
| Feed | `GET /api/feed/jsonld` | — | `JsonLdDocument[]` | 07 |
| Feed | `GET /api/feed/agent.json` | — | `AgentFeed` | 07 |

`/` and any other non-API path serve the built React app (`frontend/dist`), with `index.html` as the fallback for client-side routes. Unknown `/api/*`, `/webhooks/*` and `/health*` paths stay 404.

## Trace event schema
One `TraceEvent` per external call, recorded by the client layer and polled by the API Trace panel (about once a second).

| Field | Type | Meaning |
|---|---|---|
| `seq` | int ≥ 1 | Monotonic per process; the panel asks for `?after=<last seq>`. |
| `ts` | datetime | When the call started (UTC). |
| `service` | `paypal \| channel3 \| llm \| embeddings` | |
| `method` | str | HTTP method, or an operation name for non-HTTP clients (e.g. `embed`). |
| `endpoint` | str | Path only, e.g. `/v2/checkout/orders/{id}/capture`. No query strings, so no keys. |
| `status_code` | int? | HTTP status; null for non-HTTP calls or transport errors. |
| `duration_ms` | float ≥ 0 | Wall time, including replay lookup. |
| `cache` | `hit \| miss \| recorded \| replayed` | `replayed` = served from a fixture in replay mode; `recorded` = live call saved; `hit` = live mode reused a fixture; `miss` = replay had no fixture (an error). |
| `sandbox_ids` | `{str: str}` | Real sandbox IDs seen in the call, e.g. `{"order_id": "…", "capture_id": "…"}`. Video proof. |
| `error` | str? | Short error text; never a payload. |
| `request_id` | str? | The `X-Request-ID` of the API request that caused the call. |

**Never** in a trace event: auth headers, tokens, client secrets, API keys, full payment payloads.

## Record/replay fixture keys
Defined in `backend/app/cache/keys.py` (the transport that uses it lands in prompt 02).

- **Key** = `sha256(canonical JSON of {service, operation, query, body})`, first 16 hex chars.
- **operation** = `"METHOD /path"` for HTTP, or a named operation for non-HTTP clients (`"embed:<model>"`).
- **query**: sorted pairs; credential-bearing params (`key`, `api_key`, `apikey`, `access_token`, `client_secret`) are dropped.
- **body**: JSON compared by meaning (key order ignored); other bodies (e.g. OAuth form posts) as sorted form pairs.
- **Headers never take part** (auth and per-request IDs aren't meaning).
- **File**: `data/fixtures/<service>/<METHOD_path_slug>__<digest>.json`, human-readable for diff review.
- **Modes** (`cache_mode_for`): `replay` → fixtures only, a missing fixture is an error; `live` → `cache_first` (reuse, else call and record); `live` + `RECORD=1` → `refresh` (always call, overwrite). Writes (PayPal order create/capture, catalog PATCH) always go live outside replay.
