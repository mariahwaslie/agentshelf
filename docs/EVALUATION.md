# Evaluation

**Filled in during prompt 04 and finalized in prompt 10.** This document is what makes the impact claim honest and is a key interview talking point.

## Question
Does grounded enrichment make a merchant's products more likely to be chosen by an AI shopping agent?

## Setup
- **Catalog:** North Shore Trail Co. seed catalog, N products, version `data/catalog/seed.json@<hash>`.
- **Queries:** LLM-generated shopper intents. Train set (used during development) and **held-out set** (never used to tune enrichment or ranking). Sizes: _TBD_.
- **Competitors:** Channel3 search results per query, recorded on _date_.
- **Ranker:** fastembed model _name_ + constraint filters. Frozen before enrichment runs.
- **Baseline:** keyword (BM25-style) ranker on the same data.
- **Seeds:** `SEED=42`.

## Metrics
- **Share of shelf@k** — fraction of top-k results that are the merchant's products.
- **Recall@k** — fraction of queries where a relevant merchant product appears in top-k.
- **Mean rank** of the best merchant product.
- **Agent Visibility Score** = share of shelf@5 on held-out × 100.

## Results (held-out set)
| Condition | Share of shelf@5 | Recall@5 | Mean rank |
|---|---|---|---|
| Before enrichment | | | |
| After enrichment | | | |
| Keyword baseline (before) | | | |
| Keyword baseline (after) | | | |

## Pick-probability model
Model, features, validation method, metric (ROC AUC), feature importance chart.

## Limitations (be honest)
- Synthetic merchant catalog; real competitor data at a single point in time.
- LLM-generated intents may not match real shopper phrasing distribution.
- The golden query was chosen to illustrate; claims rest on the held-out set.
- AI shopping platforms use their own proprietary ranking; our ranker is an approximation.
