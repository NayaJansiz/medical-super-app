.PHONY: help setup dev api test lint fmt typecheck web-build check migrate migration-new seed audit hooks status

SHELL := /bin/bash

.DEFAULT_GOAL := help

help: ## Show this list
	@grep -E '^[a-z-]+:.*## ' Makefile | sed 's/:.*## /    /'

setup: ## Install Python and frontend dependencies
	uv sync
	pnpm install

dev: ## Run API (8000) and frontend (5000) together
	pnpm --dir frontend dev

api: ## Run only the API with auto-reload
	uv run uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000

test: ## Run backend tests
	uv run pytest -q

lint: ## Ruff lint and format check
	uv run ruff check .
	uv run ruff format --check .

fmt: ## Auto-fix lint and format
	uv run ruff check . --fix
	uv run ruff format .

typecheck: ## mypy on the backend
	uv run mypy backend/app

web-build: ## Type-check and build the frontend
	pnpm --dir frontend build

check: ## Everything CI runs (do this before every push)
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) test
	$(MAKE) web-build

migrate: ## Apply database migrations
	uv run alembic -c backend/alembic.ini upgrade head

migration-new: ## Create a migration: make migration-new m="add drugs"
	uv run alembic -c backend/alembic.ini revision --autogenerate -m "$(m)"

seed: ## Seed synthetic demo data (needs SEED_PASSWORD)
	PYTHONPATH=backend uv run python -m app.scripts.seed

audit: ## Audit production dependencies for known vulnerabilities
	uv export --frozen --no-hashes --no-dev -o /tmp/req-audit.txt
	uvx pip-audit -r /tmp/req-audit.txt
	pnpm audit --prod

hooks: ## Install git pre-commit hooks (one time)
	uvx pre-commit install

status: ## Plan progress and git summary (paste it to Claude)
	python3 scripts/status.py
