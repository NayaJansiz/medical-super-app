# replit.md

Follow AGENTS.md in the repo root.

- Backend: Python 3.12, FastAPI, SQLAlchemy 2 + Alembic, managed with uv.
- Frontend: React + Vite + TypeScript + Tailwind.
- Commands: `uv run pytest`, `uv run ruff check .`,
  `uv run mypy backend/app`.
- Secrets live in Replit Secrets, never in code. See .env.example.
- Start the API from the project root with
  `uv run uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000`.
- Start the API and frontend together with `pnpm --dir frontend dev`; the
  Vite page is served on port 5000 and proxies `/health` to the API.
- Apply future migrations from the project root with
  `uv run alembic -c backend/alembic.ini upgrade head`.
- Use Agent only for scaffolding, wiring and environment problems.
  One small task per prompt. Do not change files not listed.
- Do not leave deployments running during development.
