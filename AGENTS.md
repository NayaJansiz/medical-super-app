# AI working agreement (read before every task)

## Project
Medical Super App: 7 modules, synthetic data only (is_synthetic = true).
Read PROJECT_BRIEF.md, ARCHITECTURE.md, CONVENTIONS.md, SAFETY_RULES.md,
SCHEMA.md and CURRENT_PHASE.md when provided.

Stack: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 + Alembic,
PostgreSQL + pgvector, React + Vite + TypeScript + Tailwind.
Tools: uv (Python), pnpm (frontend), Ruff, mypy, pytest + httpx, Playwright.
Layout: pyproject.toml and uv.lock at the repo root; /backend (app/, tests/,
alembic/, alembic.ini), /frontend (pnpm), /docs.
Run everything from the repo root:
- Tests: `uv run pytest`
- Lint: `uv run ruff check .` and `uv run ruff format --check .`
- Types: `uv run mypy backend/app`
- API: `uv run uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000`
- API + frontend: `pnpm --dir frontend dev` (Vite on port 5000, proxies /health)
- Migrations: `uv run alembic -c backend/alembic.ini upgrade head`
- New migration: `uv run alembic -c backend/alembic.ini revision --autogenerate -m "message"`

## Rules for AI assistants
1. Work on ONE task at a time. Do not change files I did not list.
2. Ask up to 3 clarifying questions before coding if anything is ambiguous.
3. Every endpoint must state who may call it and enforce it server-side.
4. Validate all input at the boundary (Pydantic).
5. Never put secrets in code. Use environment variables.
6. Never call an AI provider directly. Use aiGateway.complete().
7. Write tests with the code: happy path, validation failure, and
   authorization (each role x endpoint).
8. Never state a drug dose or interaction as fact without a source field.
   Unverified data must be labeled "unverified" in the UI.
9. Use the error format and naming from CONVENTIONS.md.
10. Output: changed files in full, then 3 lines on how to test manually.
11. Use type hints everywhere; code must pass ruff and mypy (mypy backend/app).
12. Database changes only through Alembic migrations, never by hand.
13. Never log patient data. Medical data access goes to the audit log.
14. Synthetic data only. Never invent or request real patient data.

## Definition of Done
Acceptance criteria met, tests pass, authorization checked, no secrets,
reviewed by the other person plus a fresh AI chat, DECISIONS.md and
SCHEMA.md updated if relevant, clear commit message.
