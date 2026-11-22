# Architecture

## Stack
| Layer | Choice |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Validation | Pydantic v2 |
| Database | PostgreSQL + pgvector |
| ORM / migrations | SQLAlchemy 2 + Alembic |
| Auth | argon2 password hashing (argon2-cffi), server-side sessions in httpOnly cookies |
| Frontend | React + Vite + TypeScript + Tailwind, PWA, i18next (Arabic RTL + English) |
| Tests | pytest + httpx; Playwright for 3 flows |
| Quality | Ruff (lint + format), mypy, pip-audit |
| Dependencies | uv with a committed lock file |
| Video | Jitsi link generation only |

## Folder structure
```
/backend
  app/
    main.py
    core/        config, security, db, errors
    modules/     one folder per module (records, care, clinic,
                 pharmacy, lab, ai, education)
    ai/          aiGateway + providers (mock, gemini, groq, ...)
  alembic/
  tests/
/frontend
/docs
```

## Principles
- Client is untrusted. All rules and permissions live on the server.
- Every endpoint declares allowed roles and enforces them.
- Each module owns its tables and exposes services; modules do not reach
  into each other's tables directly.
- Contract first: the FastAPI OpenAPI spec is the contract between backend
  and frontend.

## AI Gateway
Feature code never calls an AI provider directly. It calls
`ai_gateway.complete(task, messages, schema)`, which routes to a provider
chosen by config. Providers: mock (default, canned responses), then free
tiers behind the same interface. Includes timeout, retries, quota logging,
response caching, fallback to second provider, and a kill switch.

## Auth model
Roles: patient, doctor, clinic_admin, pharmacist, student, lab_staff,
super_admin. Access to a patient's record requires either ownership or an
active, unexpired consent grant with the right scope. Every read and write
of medical data writes an audit log row.

## Deployment
Replit is for development and demos only. Config stays portable (env vars,
Docker-friendly). Migration off Replit is documented in docs/REAL_DATA.md
(Day 10).
