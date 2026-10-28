# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

The 2026 refactor of the 2024 college project into a maintained portfolio repo.

### Added

- Append-only `request_events` log written in the same transaction as every request change, with a model guard, a Postgres trigger and an idempotent backfill.
- Analytics: the `v_request_lifecycle`, `v_daily_throughput`, `v_backlog_by_status` and `v_sla_summary` views, a pure-Python lifecycle and throughput that a test reconciles with the SQL, and admin-only endpoints under `/api/v1/analytics/`.
- Parquet export (`manage.py export_analytics`) with pyarrow data contracts, a rename-based partition swap that restores the previous partition on failure, and `_run.json` run metadata.
- Service layer in `forms/services.py`, status transition rules and a permission matrix test per user group.
- Typed TypeScript API client and frontend pages wired to the API: request list, creation, detail with answer, status change and comment thread.
- Dom Bosco visual identity (logo, palette, fonts) and the unofficial-project notice on every screen and email; see `docs/BRAND.md`.
- Docker Compose stack (db, migrate, seed, api, web) with synthetic demo data, `/healthz`, and `make demo`, `smoke`, `export` and `down`.
- CI: lint (ruff, mypy strict), tests on Postgres, OpenAPI validation, frontend job and a compose smoke test.
- Security workflow (pip-audit, npm audit, zizmor) and grouped Dependabot updates.
- `docs/DECISIONS.md`, `docs/REFACTOR_PLAN.md`, `CLAUDE.md` and a rewritten README with screenshots.

### Changed

- Backend managed with uv and `pyproject.toml`; Django 5.2 LTS, DRF 3.16, psycopg 3, drf-spectacular, configuration read from the environment.
- Django project package renamed to `dombosco_service_desk`; repository named `dombosco-service-desk`.
- Frontend upgraded to Next 16 and React 19, ESLint 9 flat config, npm only, standalone build.
- Users are identified by email only; the unused `username` column was dropped.
- Staff access requires a confirmed email at the staff domain or one of its subdomains, matched on a label boundary, so a lookalike suffix no longer counts.
- Multi-stage non-root Docker images.

### Fixed

- Admin status moves stay consistent with the staff answer.
- The groups API is read-only, and the request and answer admins are read-only.
- `has_comment_permission` no longer crashes before a staff answer.
- Masked inputs keep the caret on mid-field edits and handle mobile keyboard deletes.
- Fixes brought in from the `felipe` and `Tarcisio/alteracoes` branches, with co-author credit.

### Security

- Removed the `DEBUG` permission bypass.
- `SECRET_KEY` is required and must have at least 32 characters.
- Next 14.2 had critical advisories; the upgrade to Next 16 clears them.

### Removed

- `requirements.txt`, the manual `backend/test.py` script, template leftovers, `react-input-mask` and the legacy frontend services.

## [0.1.0] - 2024-11-06

The original college version: Django REST backend and Next.js frontend for parents to open requests and staff to answer them, with JWT login and Google sign-in. Built by Emanuel Luis, Felipe (felipeoak1) and Tarcísio (tarcisio).
