# Medical Super App

Seven-module medical platform built in 10 days on synthetic data only.
Informational tool, not a diagnostic device.

## Run from a clean clone
All commands run from the repo root.
```bash
git clone <repo-url> && cd medical-super-app
cp .env.example .env            # fill in values locally, never commit
uv sync                         # Python dependencies (from uv.lock)
pnpm install    # frontend dependencies (from pnpm-lock.yaml)
uv run alembic -c backend/alembic.ini upgrade head
pnpm --dir frontend dev         # starts API + frontend; open port 5000
```
On Replit, DATABASE_URL is set automatically in Secrets.

API only:
```bash
uv run uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

## Quality checks
```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy backend/app
uv run pytest
pnpm --dir frontend build
```

## Docs
AGENTS.md (AI rules), ARCHITECTURE.md, CONVENTIONS.md, SCHEMA.md,
SAFETY_RULES.md, DECISIONS.md, PROMPTS.md, CURRENT_PHASE.md
