"""The only gateways to external services (PayPal, Channel3, LLM, embeddings).

Every call goes through the record/replay cache (app.cache) and emits a trace event (app.trace).
Built in prompts 01-02.
"""
