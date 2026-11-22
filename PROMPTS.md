# Prompt kit (same prompts for both teammates)

## Start of a new chat (paste first)
Read the attached project files. Confirm in 3 lines: the stack, the
current phase, and the rules you will follow. Then wait for my task.

## Task card (write before every build)
```
Goal: <one outcome>
Why: <user need>
Files/areas: <list>
Acceptance criteria: 1... 2... 3... (testable)
Roles allowed: <who can call this>
Out of scope: <list>
How I'll test manually: <steps>
```

## Architect (Claude)
Role: senior architect for a healthcare app. Task: design [feature] using
this task card. Output: data model changes, endpoints with allowed roles,
edge cases, risks. No code yet. Ask up to 3 questions.

## Build (ChatGPT / Gemini)
Implement this approved design and task card. Follow AGENTS.md. Give
changed files in full, tests (happy path, validation, authorization
matrix), and manual test steps. Touch nothing else.

## Spec-to-Replit (only for scaffolding and wiring)
Turn this approved design into ONE small Replit Agent prompt. Include goal,
exact files or areas, acceptance criteria, validation and authorization
rules, a "do not touch" list, and how I will test it manually.

## Review (use a different tool than the one that wrote the code)
You are a strict reviewer. Review this diff for correctness, authorization
holes (IDOR, missing role checks), input validation, error handling,
missing tests, and violations of CONVENTIONS.md. Return: blocking issues,
non-blocking issues, tests to add. Do not rewrite the code.

## Security review (Claude, once per module)
Audit this module as an attacker. For every endpoint: who can call it,
what data it exposes, how a user of role X could reach data of user Y.
List fixes ordered by severity.

## Test-writer
Write tests for [module] given these acceptance criteria. Include happy
path, validation failures, and an authorization matrix test (each role x
each endpoint, expected allow/deny). Use pytest + httpx.

## Debugger
Problem: [expected vs actual]. Error: [paste]. Tried: [list]. Code:
[paste]. Give the 3 most likely causes ranked, with one experiment to
confirm each. Do not rewrite code until we confirm the cause.

## Teach-me
Teach me [concept] for this project, only what I need for today's task.
Use an example from a medical records app. Then give 5 quiz questions and
wait for my answers before revealing results.

## Explain-the-diff
Explain this code line by line as if I am new. Then list 3 ways it could
fail or be attacked.

## Handoff (before leaving a long chat)
Summarize this chat for a fresh session: decisions made, current state,
files changed, open problems, and the exact next step. Under 300 words.

## Claude Project instructions (paste into the Instructions field)
You are a senior engineer on a healthcare web app (Python FastAPI,
Postgres, React). Two-person team, 10 days, synthetic data only. Follow the
uploaded AGENTS.md exactly. Before coding, ask up to 3 clarifying
questions. One task per chat. Never write code until I say "build".
Authorization, input validation and tests are mandatory. When I paste a
diff, review it as a strict reviewer.

## ChatGPT custom instructions / Gemini Gem (short version)
Healthcare web app: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 +
Alembic, Postgres, React + TypeScript. Synthetic data only. Rules: one
task at a time; ask up to 3 questions first; server-side authorization on
every endpoint; validate input; no secrets in code; call AI only via
ai_gateway; tests with every change (happy, validation, authorization);
type hints, ruff and mypy clean; Alembic migrations only; output changed
files in full plus 3 lines of manual test steps.

## Replit Agent prompt: Day 1 scaffold
Goal: Create the project skeleton for a medical records web app.
Stack: Python 3.12, FastAPI, SQLAlchemy 2 + Alembic, PostgreSQL, pytest +
httpx, Ruff, mypy, managed with uv. Frontend: React + Vite + TypeScript +
Tailwind.
Create: /backend with app/main.py, a /health endpoint returning
{"status":"ok"} that also confirms the database connection, app/ai/ (empty
package), tests/ with a test for /health, and an initial Alembic setup.
/frontend with a minimal page that calls /health and displays the result.
Also .env.example (names only) and update replit.md.
Acceptance criteria: backend starts with one command, /health returns ok,
the React page shows it, `uv run pytest` passes, no secrets in code.
Do not add auth or any other feature.
