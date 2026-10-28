# Decisions

Decisions taken while turning the college project into a maintained portfolio repo. Newest last.

| # | Date | Decision | Choice | Why |
| --- | --- | --- | --- | --- |
| 1 | 2026-10-27 | Visibility and identity | Public portfolio repo; keep the school name, the domain and the college team origin; credit the team in the README | It is a real team project and reads best with its context intact |
| 2 | 2026-10-28 | Repository name | `programacao_web` renamed to `dombosco-service-desk` (an interim `dombosco-atendimento` name was dropped) | An English name that says what the app is; the Django project package follows when the settings are rewritten, if the rename stays cheap |
| 3 | 2026-10-28 | Secret scan before going public | gitleaks over every ref plus a manual sweep of every blob: no live secret, no real people's data. Dev-only values that sat in history (the Django `django-insecure-` startproject key, the local compose Postgres password, test-script passwords) are treated as burned and never reused | A public history cannot be unpublished |
| 4 | 2026-10-28 | Unmerged teammate branches (`felipe`, `Tarcisio/alteracoes`) | Bring in the useful fixes with `Co-authored-by` credit (PR #3) instead of merging the branches as they are; keep both branches | The `felipe` super-user screen keyed on the wrong group and sent edits to an endpoint that ignores them; the `Tarcisio/alteracoes` redirect sent signed-in users home on every reload |
| 5 | 2026-10-28 | Commit identities | History rewritten once so the owner's commits use his personal address (author and committer); two older personal addresses in a test script were replaced too; teammates' identities untouched | Personal portfolio identity; pull-request refs that keep the old commits go to GitHub Support |
| 6 | 2026-10-28 | Old branch protection on `main` | Removed for the one rewrite push; the portfolio protection (required CI checks, no force-push or deletion) is applied once the repo is public | A force-push is impossible under the old rule; until then changes reach `main` only through PRs with green CI and review |
