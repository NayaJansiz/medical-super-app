# Conventions

## Git
- Trunk-based: `main` always works. No direct pushes to main.
- Branches: feat/<name>, fix/<name>, docs/<name>, chore/<name>, test/<name>
- Commits: `type: short message` (feat, fix, docs, test, chore)
  e.g. `feat: add patient profile endpoint`
- One PR = one outcome. Squash merge. Another person approves.
- If a diff takes more than 15 minutes to review, split it.

## Code
- Python 3.12, type hints everywhere. Must pass `ruff check`, `ruff format`
  and `mypy app`.
- Naming: snake_case in Python and database, camelCase only in frontend.
- Tables: plural snake_case (patients, appointments). Every table has
  id, created_at, updated_at. Seeded rows have is_synthetic = true.
- Database changes only via Alembic migrations.

## API style
- REST, JSON, prefix /api/v1.
- Every endpoint: declared allowed roles, Pydantic request and response
  models, tests for allow and deny.
- Error format (always):
```json
{"error": {"code": "FORBIDDEN", "message": "Human readable", "details": null}}
```
- Status codes: 400 validation, 401 not logged in, 403 not allowed,
  404 not found (also used to avoid leaking that a record exists), 409
  conflict (e.g. double booking), 429 rate limited.
- Never return password hashes, tokens, or other users' data.

## Security
- No secrets in code. `.env.example` lists names only.
- No patient data in logs. Medical data access goes to the audit log.
- Validate input at the boundary. Limit upload size and type.

## Tests
- Each PR: unit + integration tests, plus the authorization matrix test.
- Golden set for the AI assistant runs on every prompt or model change.
- A bug gets a failing test first, then the fix.

## AI usage
- One chat, one deliverable. New chat after about 15 to 20 exchanges.
- The tool that reviews must differ from the tool that wrote the code.
- Paste only the files relevant to the task.
