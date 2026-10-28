.DEFAULT_GOAL := help
.PHONY: help install fmt lint test-fast frontend-install frontend-lint frontend-test frontend-build up down logs demo smoke export

help: ## Show this help
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "%-12s %s\n", $$1, $$2}'

install: ## Install backend dependencies from the lockfile
	cd backend && uv sync --locked --extra export

fmt: ## Format and autofix the backend
	cd backend && uv run ruff check --fix . && uv run ruff format .

lint: ## Ruff check, format check and mypy (same as CI lint)
	cd backend && uv run ruff check . && uv run ruff format --check . && SECRET_KEY=$${SECRET_KEY:-mypy-only-not-secret-0123456789abcdef} uv run mypy .

test-fast: ## Run the backend tests on SQLite
	cd backend && uv run pytest

frontend-install: ## Install frontend dependencies from the lockfile
	cd frontend && npm ci

frontend-lint: ## ESLint and tsc (same as CI frontend)
	cd frontend && npm run lint && npx tsc --noEmit

frontend-build: ## Production build of the frontend
	cd frontend && npm run build

frontend-test: ## Unit tests of the frontend (vitest)
	cd frontend && npm test

up: ## Start the stack in the background (needs .env, see make demo)
	docker compose up -d --wait --build

down: ## Stop the stack and delete its volumes (demo data included)
	docker compose down -v

logs: ## Follow the stack logs
	docker compose logs -f

demo: ## One command: create .env if missing, build, start, print URLs and logins
	@test -f .env || { cp .env.example .env && 		sed -i.bak "s|^SECRET_KEY=.*|SECRET_KEY=$$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))' 2>/dev/null || python -c 'import secrets; print(secrets.token_urlsafe(50))')|" .env && rm -f .env.bak; }
	docker compose up -d --wait --build
	@echo ""
	@echo "Web: http://localhost:3000   API: http://localhost:8000/swagger/"
	@echo "Demo logins (password: DEMO_PASSWORD in .env, default demo-only-change-me):"
	@echo "  admin@demo.example, staff1@demo.example, parent1@demo.example"

smoke: ## HTTP checks against the running stack
	sh scripts/smoke.sh

export: ## Export the analytics Parquet files to ./exports
	mkdir -p exports && chmod a+rwx exports
	docker compose exec api python manage.py export_analytics --as-of $$(date -u +%F) --out /exports
