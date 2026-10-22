# AgentShelf — common commands. Prompt 00 makes every target work; adjust paths there if the plan changes.
.PHONY: help setup dev check lint typecheck test golden e2e types types-check record eval demo keys-check deploy-check clean

BACKEND := backend
FRONTEND := frontend
OPENAPI := cd $(BACKEND) && uv run python -m app.export_openapi > ../$(FRONTEND)/openapi.json
UVICORN := uv run uvicorn --factory app.main:create_app --no-access-log

help: ## List commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

setup: ## Install backend + frontend deps and pre-commit hooks
	cd $(BACKEND) && uv sync
	cd $(FRONTEND) && npm ci
	uv tool install --quiet pre-commit
	uv tool run pre-commit install

dev: ## Run backend (reload) and frontend dev server
	@echo "Backend :8000  Frontend :5173"
	cd $(BACKEND) && $(UVICORN) --reload --port 8000 & \
	cd $(FRONTEND) && npm run dev

lint: ## Lint and format-check both sides
	cd $(BACKEND) && uv run ruff check . && uv run ruff format --check .
	cd $(FRONTEND) && npm run lint && npm run format:check

typecheck: ## Static types (mypy strict on core, tsc strict)
	cd $(BACKEND) && uv run mypy app
	cd $(FRONTEND) && npm run typecheck

test: ## Unit + contract tests with coverage on core (replay mode, no network)
	cd $(BACKEND) && APP_MODE=replay uv run pytest tests/unit tests/contract --cov=app/domain --cov=app/clients --cov=app/cache --cov=app/trace --cov=app/api --cov-fail-under=80

golden: ## Golden demo path test (replay mode)
	cd $(BACKEND) && APP_MODE=replay uv run pytest tests/golden -v

types: ## Regenerate frontend API types from backend OpenAPI
	$(OPENAPI)
	cd $(FRONTEND) && npx openapi-typescript openapi.json -o src/api/types.gen.ts

types-check: ## Fail if the committed frontend API types are stale (fix: make types)
	$(OPENAPI)
	cd $(FRONTEND) && npx openapi-typescript openapi.json -o .types-check.gen.ts
	@cd $(FRONTEND) && if cmp -s src/api/types.gen.ts .types-check.gen.ts; then rm .types-check.gen.ts; \
	else rm .types-check.gen.ts; echo "src/api/types.gen.ts is stale: run 'make types' and commit it"; exit 1; fi

check: lint typecheck test golden types-check ## Everything CI runs

e2e: ## Playwright smoke test of the golden path (replay mode)
	cd $(FRONTEND) && npx playwright test

record: ## Re-record external API fixtures in live mode (review the diff before committing!)
	cd $(BACKEND) && APP_MODE=live RECORD=1 uv run python -m app.scripts.record_fixtures

eval: ## Reproduce the numbers in docs/EVALUATION.md
	cd $(BACKEND) && APP_MODE=replay uv run python -m app.scripts.run_eval

demo: ## Run the full app in replay mode — no keys needed
	cd $(FRONTEND) && npm run build
	@echo "Open http://localhost:8000 (Ctrl+C to stop)"
	cd $(BACKEND) && APP_MODE=replay DISPLAY_ANONYMIZED=true $(UVICORN) --port 8000

keys-check: ## Report which keys are present in .env (never prints values)
	cd $(BACKEND) && uv run python -m app.scripts.keys_check

deploy-check: ## Build the production Docker image locally
	docker build -t agentshelf .

clean: ## Remove build artifacts
	rm -rf $(FRONTEND)/dist $(BACKEND)/.pytest_cache $(BACKEND)/.mypy_cache $(BACKEND)/.ruff_cache
