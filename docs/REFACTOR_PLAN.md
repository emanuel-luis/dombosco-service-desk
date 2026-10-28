# Refactor plan

Plan for turning the 2024 college project into a maintained portfolio repo. Each step ships as a
small PR that merges only with green CI and a review. Status is in the table below ("done locally" means committed on a branch, not yet pushed or merged); decisions live
in [DECISIONS.md](DECISIONS.md).

## PR sequence

| # | Branch | What | CI it adds | Status |
| --- | --- | --- | --- | --- |
| 1 | `refactor/backend-baseline` | `backend/pyproject.toml` + `uv.lock` (current pins), ruff (line length 100, `BLE`) and `ruff format`, pytest-django smoke tests, Makefile (`help`, `install`, `lint`, `test-fast`), delete `requirements.txt`, `ruff.toml`, the manual `backend/test.py` script and dead files | `lint`, `test` (Postgres service, `manage.py check`, `makemigrations --check`) | done locally |
| 2 | PR #3 | Teammate fixes (frontend only), rebased on 1 | — | open as PR #3 |
| 3 | `refactor/settings-deps` | Django project package renamed to `dombosco_service_desk` (if cheap), Django 5.2 LTS, DRF 3.16, psycopg 3, drf-spectacular, pydantic-settings config (`SECRET_KEY` required, `DEBUG` off by default, hosts/CORS/CSRF/DB from env), `.env.example`, remove the DEBUG permission bypass | — | done locally |
| 4 | `refactor/request-lifecycle` | `forms/services.py` (all writes, one transaction each), status transition rules, bug fixes, permission matrix tests per group, groups on `/auth/user/`, mypy strict in `lint` | mypy | done locally |
| 5 | `feat/request-events` | Append-only `request_events` log, immutability guard (model + Postgres trigger), idempotent backfill | — | done locally |
| 6 | `feat/analytics` | SQL views (lifecycle, daily throughput, backlog, SLA), admin-only endpoints, optional Parquet export with contract checks and run metadata | — | done locally |
| 7 | `refactor/frontend-build` | `next build` green on Next 14.2, npm only, template leftovers removed, `output: "standalone"` | `frontend` | done locally |
| 8 | `feat/frontend-brand` | Dom Bosco visual identity: the official logo, palette and typography from the institution's site as Tailwind/CSS tokens (WCAG AA checked), `docs/BRAND.md`, and the notice that this is an unofficial academic project in every footer, on the login screen and in the README | — | done locally |
| 9 | `feat/frontend-wiring` | Pages wired to the API, roles from `/auth/user/`, API URL and Google client ID from env, comment thread | — | done locally |
| 10 | `refactor/docker` | Multi-stage non-root images, one `compose.yaml` (db, migrate, seed, api, web), synthetic demo seed, `make up/down/demo` | `compose-smoke` | done locally |
| 11 | `ci/security` | `security.yml` (pip-audit, npm audit, zizmor), Dependabot | — | done locally |
| 12 | `docs/readme` | README (with branded screenshots), CLAUDE.md, CHANGELOG, LICENSE, D2 diagrams | `diagrams` | in progress: README, CLAUDE.md, CHANGELOG and D2 diagrams done; LICENSE pending the co-authors' agreement |
| 13 | `chore/next-upgrade` | Next 16, React 19, Node 24 LTS, eslint 9 flat config | — | done locally |

## Data flow (layers)

- **source**: OLTP tables `forms_parentform`, `forms_staffform`, `forms_comment`, written only
  through `forms/services.py`.
- **raw**: `request_events`, one immutable row per lifecycle event (who, role, UTC time,
  from/to status), written in the same transaction as the domain change.
- **processed**: `v_request_lifecycle`, one row per request (opened, first response, closed,
  hours to first response and to close).
- **serving**: `v_daily_throughput`, `v_backlog_by_status`, `v_sla_summary`, exposed to
  administrators under `/api/v1/analytics/`, plus an optional Parquet snapshot
  (`manage.py export_analytics --as-of <date>`) checked against a pyarrow contract and written
  atomically with a `_run.json` (run id, UTC timestamps, row counts).

## Testing

`make test-fast` runs pytest on SQLite without Docker; Postgres-only tests (trigger, views) carry
the `postgres` marker and run in CI against a Postgres service, or locally with `DATABASE_URL`
pointing at a Postgres. There is no make target for them.
