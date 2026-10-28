# CLAUDE.md

Django 5.2 + DRF backend (`backend/`), Next.js 16 frontend (`frontend/`), Postgres, Docker Compose. Public, unofficial school service desk.

## Commands

- `make install lint test-fast`: backend deps, ruff + mypy strict, pytest on SQLite.
- Postgres-only tests (trigger, analytics views) run in CI or with `DATABASE_URL` pointing at a Postgres.
- `make frontend-install frontend-lint frontend-test frontend-build`: frontend.
- `make demo`, `make smoke`, `make export`, `make down`: Docker stack (do not run Docker unless asked).

## Repo map

- `backend/dombosco_service_desk/`: settings (env via `config.py`), urls, `/healthz`.
- `backend/core/`: users (email only), groups, permissions, staff-domain signal.
- `backend/forms/`: requests, comments, `services.py` (all writes), `RequestEvent`, backfill, `seed_demo`.
- `backend/analytics/`: SQL views (migration 0001), `lifecycle.py`, `throughput.py`, contracts, Parquet export, admin endpoints.
- `frontend/app/lib/`: typed API client, roles, errors, masks.
- `docs/`: DECISIONS.md, REFACTOR_PLAN.md, BRAND.md, screenshots.

## Invariants

- Every request write goes through `forms/services.py`, one transaction, with its event.
- `request_events` is append-only (model guard and Postgres trigger). Never update or delete rows.
- The analytics SQL and `analytics/lifecycle.py` / `throughput.py` must stay equal; the Postgres reconciliation tests enforce it.
- Seed and demo data are synthetic only. Never add real people's data.
- UI text is pt-BR and the unofficial-project notice stays on every screen and email.

## Conventions

- ruff (line length 100) and mypy strict; ESLint 9 and tsc for the frontend.
- Conventional Commits in English; PR descriptions in pt-BR.
- No secrets in code; configuration comes from the environment (`.env.example`).
