.DEFAULT_GOAL := help
.PHONY: help install fmt lint test-fast frontend-install frontend-lint frontend-test frontend-build

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
