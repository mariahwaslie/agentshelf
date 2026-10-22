# 0001 — Technology stack

- **Date:** 2026-10-22 (proposed in the kit; reviewed and amended in prompt 00)
- **Status:** accepted

## Context
Solo entrant, ~3 weeks, code written by Claude Code, $0 budget, Render free tier (512 MB RAM), sponsor tools are React-first, Mariah's strength is Python/ML.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| Python FastAPI + React (single service) | Plays to Python/ML strength; React matches AG Grid/AG Studio; one deploy | Two languages |
| All TypeScript (Next.js) | One language | ML in a weaker ecosystem; less of Mariah's story |
| Two services (API + static site) | Clean separation | Two cold starts, CORS, more config |

Per-component choices reviewed in prompt 00 (two options each):

| Choice | Chosen | Rejected | Why |
|---|---|---|---|
| Web framework | **FastAPI** | Litestar | Built-in OpenAPI drives the generated TypeScript types; widely known. |
| Persistence | **SQLAlchemy 2.0 typed ORM** + separate Pydantic contracts | SQLModel | SQLModel `table=True` models skip validation, so nested JSON (attributes, grounding spans) loads as raw dicts typed as models; friction with mypy strict. Separate models keep the fixed contracts independent of storage. |
| Embeddings | **fastembed** (`bge-small-en-v1.5`, ONNX) | model2vec static embeddings | Better retrieval quality. model2vec (~30 MB) is the fallback if spike 01 shows fastembed too heavy for 512 MB (risk R5). |
| LLM SDK | **Plain httpx** to Gemini REST (JSON `responseSchema`) | google-genai SDK | One transport for PayPal, Channel3 and Gemini means one record/replay, trace and retry mechanism, and an easy provider swap. |
| Frontend build | **Vite + React SPA** + openapi-fetch + TanStack Query | Next.js | Static `dist/` served by FastAPI keeps one service; SSR isn't needed. |
| Tests / fixtures | **pytest + our own record/replay layer** | pytest + vcrpy cassettes | Tests exercise the same replay path demo mode uses. |

## Decision
Python 3.12 FastAPI backend serving a React + Vite + TypeScript frontend from one Docker container on Render. fastembed (ONNX) for embeddings to stay under 512 MB. Gemini free tier for in-app LLM calls via plain httpx, with full record/replay caching. SQLite via SQLAlchemy 2.0, seeded on boot. Sync route handlers and sync `httpx.Client` (FastAPI runs them in a threadpool); the API Trace panel polls instead of streaming.

## Amendments made during prompt 00 setup
- **TypeScript 5.9, not 6.0.** The Vite 8 template ships TS 6.0, but openapi-typescript 7.13 (latest) declares support for TS 5 only. Pinning 5.9 avoids forcing peer dependencies.
- **ESLint + typescript-eslint (strict, type-checked), not oxlint.** The template now defaults to oxlint; `docs/STANDARDS.md` specifies ESLint + Prettier.
- **httpx stays; httpx2 deferred.** Starlette 1.9's TestClient prefers `httpx2` (a successor to httpx published under the Pydantic GitHub org) and warns on httpx. Adding it was blocked pending vetting, so the project stays on httpx 0.28.1 and the test config ignores that one warning. Revisit if Mariah approves httpx2 after checking it.
- **CI on Node 24-era action majors** (`checkout@v7`, `setup-node@v7`, `setup-python@v7`, `setup-uv@v10`, `gitleaks-action@v3`). Node 20 actions stopped working on GitHub runners on Sept 16, 2026.

## Consequences
Easy single deploy and judge-friendly URL. Memory must be watched (spike check). Types generated from OpenAPI to avoid drift between languages. Every external call shares one interception point (the httpx transport), so record/replay and tracing can't be bypassed. A small mapping layer is needed between DB rows and contract models.
