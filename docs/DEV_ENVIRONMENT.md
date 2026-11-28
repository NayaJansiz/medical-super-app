# Working without Replit

Replit Core ends on **Thu 3 Dec**. Nothing in this repo needs Replit. Both of
us should be able to run the project somewhere else by **Fri 27 Nov evening**,
well before the deadline.

## What the free options give (checked 27 Nov 2026)
- **Replit free (Starter):** still exists, but with daily Agent credits,
  limited monthly cloud credits, Lite build only and one published app. Fine
  as a fallback editor, not as the main environment.
- **GitHub Codespaces:** each personal GitHub Free account gets 120 core-hours
  and 15 GB of storage a month. A 2-core codespace gets about 60 hours. Stop it
  when you are not working (it also stops itself after idle time). Quotas are
  per person, and each person uses their own.
- **GitHub Actions:** standard runners are free for public repositories, and
  this repository is public.
- **Neon Postgres (optional):** free plan with 100 projects, 1 GB storage each,
  scale to zero after 5 minutes idle, no card. Only needed for the local
  route below.

Availability of Codespaces, Neon and every AI provider from your location is
not verified. Check each with the VPN off (PLAN.md, Fri 27 Nov).

## Route A: GitHub Codespaces (recommended)
1. On the repo page: Code, Codespaces, Create codespace on main. The first
   build takes a few minutes: it installs Python, Node, pnpm, uv, starts a
   Postgres 16 container with pgvector, installs dependencies and runs the
   migrations.
2. In the terminal: `make dev`. Open the forwarded ports: 5000 (web) and 8000 (API).
3. Seed demo data: `SEED_PASSWORD='long-password-you-choose' make seed`.
4. Secrets go in GitHub, Settings, Codespaces, Secrets (for example
   `SEED_PASSWORD` or provider API keys). Never in a file in the repo.
5. Push and open PRs from the codespace. `gh` is installed.

## Route B: your own computer (Windows)
1. Install Git, Python 3.12, Node 20, and `uv` (`winget install astral-sh.uv`).
   Install pnpm (`npm i -g pnpm@9`). `make` is easiest inside WSL or Git Bash;
   without it, run the commands from the Makefile by hand.
2. Database: either Docker Desktop and
   `docker compose -f .devcontainer/docker-compose.yml up db` (then
   `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app` after
   adding `ports: ["5432:5432"]` to the db service), or a free Neon project:
   copy its connection string into `.env` as `DATABASE_URL`.
3. `cp .env.example .env`, fill in values (the file is git-ignored), then
   `make setup`, `make migrate`, `make dev`.

## Route C: Replit Starter (fallback)
Import the repo again. Expect limits. Do not rely on it.

## Leaving-Replit checklist
- [ ] Both: Route A or B runs `make check` green
- [ ] Both: `make dev` shows the app and you can log in as `patient@demo.example`
- [ ] Any secret you only had in Replit Secrets is now in Codespaces secrets or `.env`
- [ ] `git status` is clean in Replit and everything is pushed to GitHub
- [ ] CI is green on main without Replit involved
