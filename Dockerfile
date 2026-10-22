# syntax=docker/dockerfile:1
# One image, one service: FastAPI serves the API and the built React app (docs/ARCHITECTURE.md).

# --- Stage 1: build the frontend ---
FROM node:22-slim AS frontend
WORKDIR /srv/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: slim Python runtime ---
FROM python:3.12-slim AS runtime
COPY --from=ghcr.io/astral-sh/uv:0.13.3 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/srv/.venv \
    PYTHONUNBUFFERED=1
WORKDIR /srv/backend
COPY backend/pyproject.toml backend/uv.lock backend/.python-version ./
RUN uv sync --locked --no-dev
COPY backend/app ./app
COPY data /srv/data
COPY --from=frontend /srv/frontend/dist /srv/frontend/dist

# The app user may write only to backend/var (SQLite lives there; see settings.var_dir).
RUN useradd --create-home --uid 10001 app && mkdir -p /srv/backend/var && chown app /srv/backend/var
USER app

# Replay mode by default: judges can run the image with no keys. Render overrides via env.
ENV APP_MODE=replay \
    LOG_JSON=true \
    PORT=8000 \
    PATH="/srv/.venv/bin:$PATH"
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn --factory app.main:create_app --host 0.0.0.0 --port ${PORT} --no-access-log"]
