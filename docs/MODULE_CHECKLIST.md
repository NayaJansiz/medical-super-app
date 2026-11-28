# Adding a module (follow the pattern already in the repo)

Copy the shape of `backend/app/modules/records/` (models, schemas, service,
router) and its tests. Every module needs all of these.

## Backend
1. `backend/app/modules/<name>/` with `__init__.py`, `models.py`,
   `schemas.py`, `service.py`, `router.py`. Business rules live in `service.py`;
   the router only translates HTTP.
2. Models inherit `Base` (`app/db/base.py`). Give seeded rows an
   `is_synthetic` column. Medical facts carry a `source` and a verification
   status; anything unverified is returned as `unverified`.
3. Register it: import the models in `backend/app/db/models.py` and add
   `app.include_router(...)` in `backend/app/main.py`.
4. Migration: `make migration-new m="add <name> tables"`, then read the
   generated file and fix it by hand (names, indexes, constraints). `make migrate`.
   Add the table to `SCHEMA.md`.
5. Router: `APIRouter(prefix="/api/v1")`. Use `DbSession`, `CurrentUser` and
   `require_roles(Role.X, ...)` from `app.modules.auth.deps`. Every endpoint says
   in its docstring who may call it.
6. Errors: raise `AppError(status, "CODE", "message")` (`app.core.errors`).
   Record not found or not yours: 404 with the same message for both.
7. Audit: reads and writes of medical data call `audit.log(...)`
   (`app.modules.audit.service`). The caller commits. Denied attempts are
   logged too, then committed before raising.
8. Seed: add fake rows (`is_synthetic=True`) to `backend/app/scripts/seed.py`.

## Tests (copy the style of `test_records_matrix.py`)
- Fixtures `client`, `engine`, `make_user` live in `backend/tests/conftest.py`;
  helpers such as `login` in `backend/tests/helpers.py`.
- Happy path, validation failure, and an authorization matrix: every role
  against every endpoint, with the expected allow or deny.
- IDOR: user A asks for user B's record and gets 404.
- Anything with a rule (interaction checker, range flags, booking state
  machine, quiz scoring) gets table-driven unit tests with boundary values.
- `make check` before every push.

## Frontend
1. API calls and types: `frontend/src/api/` (`client.ts`, `types.ts`).
2. Page in `frontend/src/pages/`, route in `frontend/src/App.tsx`.
3. Text in both `frontend/src/i18n/en.json` and `ar.json`. No hard-coded strings.
4. RTL: use logical Tailwind classes (`ms-`, `me-`, `ps-`, `pe-`, `text-start`),
   never `ml-`, `mr-`, `text-left`. Check the page in Arabic.
5. Show the API's error `message`; handle 401 (log in again) and 403.
6. Works at 360px width. `pnpm --dir frontend build` passes.

## Done means
Plan item ticked, tests green, authorization matrix included, migration
reviewed, SCHEMA.md updated, PR describes how to test it.
