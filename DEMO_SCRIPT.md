# Demo Script (target 2:45, hard limit 3:00)

Locked early so every build session knows what must look good on camera. Change only with a note in `docs/PROGRESS.md`.

**Setup before recording:** replay or live mode decided; anonymized display ON; Reset demo clicked; browser at 1440×900; API Trace panel visible; sandbox buyer logged out; no bookmarks/tabs with personal info; captions on.

| Time | Scene | On screen | Voiceover (draft) |
|---|---|---|---|
| 0:00–0:20 | Problem | Title card → one stat | "AI agents are now a sales channel. But PayPal's own research says only about one in five merchants have catalogs agents can actually read." |
| 0:20–0:35 | Meet the shop | North Shore Trail Co. catalog imported; PayPal product IDs appear in API Trace | "This is a small Minnesota outdoor shop on PayPal. AgentShelf syncs its catalog to PayPal…" |
| 0:35–0:55 | Benchmark | Visibility Score low; golden query result: Competitor A wins | "…and tests it against real competitor listings from Channel3, the way a shopping agent would. Right now, agents pick the competitor." |
| 0:55–1:30 | Fix | Gap diagnosis → enrichment diffs in AG Grid → hover shows grounding evidence → Approve → PayPal catalog update in trace | "AgentShelf finds what's missing, proposes fixes grounded in the merchant's own product text — no invented claims — and she approves them." |
| **1:30–2:15** | **The flip (wow moment)** | Split view: same golden query before vs. after → shopper agent now picks her boot → PayPal order → buyer approves with Pay Later visible → capture → webhook → "agent-sourced revenue" ticks up | "Same request, same agent. Now it picks her product, creates a PayPal order, the buyer approves, and the webhook records it as agent-sourced revenue." |
| 2:15–2:35 | Proof + dashboard | Held-out metrics before/after vs. baseline; dashboard; Studio agent answer | "Across held-out shopper queries, her share of shelf rose from X% to Y%." |
| 2:35–2:45 | Close | Logo + one line | "Store Sync distributes your catalog. AgentShelf makes sure agents choose it — and proves it with PayPal." |

**Golden query (draft, lock in prompt 03):** "waterproof wide-fit hiking boots under $120"
