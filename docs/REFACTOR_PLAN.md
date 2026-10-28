# Refactor plan

Plan for turning the 2024 college project into a maintained portfolio repo. Each step ships as a
small PR that merges only with green CI and a review. Status is tracked in the PRs; decisions live
in [DECISIONS.md](DECISIONS.md).

## PR sequence

| # | Branch | What | CI it adds |
| --- | --- | --- | --- |
| 1 | `refactor/backend-baseline` | `backend/pyproject.toml` + `uv.lock` (current pins), ruff (line length 100, `BLE`) and `ruff format`, pytest-django smoke tests, Makefile (`help`, `install`, `lint`, `test-fast`), delete `requirements.txt`, `ruff.toml`, the manual `backend/test.py` script and dead files | `lint`, `test` (Postgres service, `manage.py check`, `makemigrations --check`) |
| 2 | PR #3 | Teammate fixes (frontend only), rebased on 1 | — |
| 3 | `refactor/settings-deps` | Django project package renamed to `dombosco_service_desk` (if cheap), Django 5.2 LTS, DRF 3.16, psycopg 3, drf-spectacular, pydantic-settings config (`SECRET_KEY` required, `DEBUG` off by default, hosts/CORS/CSRF/DB from env), `.env.example`, remove the DEBUG permission bypass | — |
| 4 | `refactor/request-lifecycle` | `forms/services.py` (all writes, one transaction each), status transition rules, bug fixes, permission matrix tests per group, groups on `/auth/user/`, mypy strict in `lint` | mypy |
| 5 | `feat/request-events` | Append-only `request_events` log, immutability guard (model + Postgres trigger), idempotent backfill | — |
| 6 | `feat/analytics` | SQL views (lifecycle, daily throughput, backlog, SLA), admin-only endpoints, optional Parquet export with contract checks and run metadata | — |
| 7 | `refactor/frontend-build` | `next build` green on Next 14.2, npm only, template leftovers removed, `output: "standalone"` | `frontend` |
| 8 | `feat/frontend-brand` | Dom Bosco visual identity: the official logo, palette and typography from the institution's site as Tailwind/CSS tokens (WCAG AA checked), `docs/BRAND.md`, and the notice that this is an unofficial academic project in every footer, on the login screen and in the README | — |
| 9 | `feat/frontend-wiring` | Pages wired to the API, roles from `/auth/user/`, API URL and Google client ID from env, comment thread | — |
| 10 | `refactor/docker` | Multi-stage non-root images, one `compose.yaml` (db, migrate, seed, api, web), synthetic demo seed, `make up/down/demo` | `compose-smoke` |
| 11 | `ci/security` | `security.yml` (pip-audit, npm audit, zizmor), Dependabot | — |
| 12 | `docs/readme` | README (with branded screenshots), CLAUDE.md, CHANGELOG, LICENSE, D2 diagrams | `diagrams` |
| 13 | `chore/next-upgrade` | Next 16, React 19, Node 24 LTS, eslint 9 flat config | — |

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
the `postgres` marker and run in CI against a Postgres service and locally through
`make test` (compose `db`).
