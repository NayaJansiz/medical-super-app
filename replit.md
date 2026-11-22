# replit.md

Follow AGENTS.md in the repo root.

- Backend: Python 3.12, FastAPI, SQLAlchemy 2 + Alembic, managed with uv.
- Frontend: React + Vite + TypeScript + Tailwind.
- Commands: `uv run pytest`, `uv run ruff check .`, `uv run mypy app`.
- Secrets live in Replit Secrets, never in code. See .env.example.
- Use Agent only for scaffolding, wiring and environment problems.
  One small task per prompt. Do not change files not listed.
- Do not leave deployments running during development.
