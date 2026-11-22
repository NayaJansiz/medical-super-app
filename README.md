# Medical Super App

Seven-module medical platform built in 10 days on synthetic data only.
Informational tool, not a diagnostic device.

## Run from a clean clone
```bash
git clone <repo-url> && cd medical-super-app
cp .env.example .env        # fill in values locally, never commit
cd backend && uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
# in another terminal
cd frontend && npm install && npm run dev
```

## Quality checks
```bash
cd backend
uv run ruff check . && uv run ruff format --check .
uv run mypy app
uv run pytest
```

## Docs
AGENTS.md (AI rules), ARCHITECTURE.md, CONVENTIONS.md, SCHEMA.md,
SAFETY_RULES.md, DECISIONS.md, PROMPTS.md, CURRENT_PHASE.md
