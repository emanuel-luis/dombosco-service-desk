.DEFAULT_GOAL := help
.PHONY: help install fmt lint test-fast

help: ## Show this help
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "%-12s %s\n", $$1, $$2}'

install: ## Install backend dependencies from the lockfile
	cd backend && uv sync --locked

fmt: ## Format and autofix the backend
	cd backend && uv run ruff check --fix . && uv run ruff format .

lint: ## Ruff check and format check (same as CI lint)
	cd backend && uv run ruff check . && uv run ruff format --check .

test-fast: ## Run the backend tests on SQLite
	cd backend && uv run pytest
