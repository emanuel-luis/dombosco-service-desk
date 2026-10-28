#!/bin/sh
# HTTP checks against a running stack (make demo / make up). Needs curl and python3.
set -eu
# Git Bash would rewrite container paths such as /tmp/exports into Windows paths.
export MSYS_NO_PATHCONV=1

API=${API_URL:-http://localhost:8000}
WEB=${WEB_URL:-http://localhost:3000}
PASSWORD=${DEMO_PASSWORD:-demo-only-change-me}
if [ -z "${DEMO_PASSWORD:-}" ] && [ -f .env ]; then
  PASSWORD=$(sed -n 's/^DEMO_PASSWORD=//p' .env | tail -n 1)
  PASSWORD=${PASSWORD:-demo-only-change-me}
fi

fail() { echo "FAIL: $*" >&2; exit 1; }

status() { curl -s -o /dev/null -w '%{http_code}' "$@"; }

token() {
  body=$(printf '{"email":"%s","password":"%s"}' "$1" "$PASSWORD")
  curl -sf -X POST -H 'Content-Type: application/json' -d "$body" "$API/api/v1/auth/login/" |
    python3 -c 'import json, sys; print(json.load(sys.stdin)["access"])'
}

[ "$(status "$API/healthz")" = 200 ] || fail "/healthz is not 200"
echo "ok healthz"

parent=$(token parent1@demo.example) || fail "parent login"
count=$(curl -sf -H "Authorization: Bearer $parent" "$API/api/v1/forms/parent/" |
  python3 -c 'import json, sys; print(len(json.load(sys.stdin)))') || fail "list requests"
[ "$count" -gt 0 ] || fail "demo parent has no requests"
echo "ok parent sees $count requests"

admin=$(token admin@demo.example) || fail "admin login"
[ "$(status -H "Authorization: Bearer $admin" "$API/api/v1/analytics/sla/")" = 200 ] ||
  fail "analytics/sla is not 200"
echo "ok analytics sla"

[ "$(status "$WEB/login")" = 200 ] || fail "web /login is not 200"
echo "ok web login"

# The export runs in the container and the partition is copied out: no bind mount, so no
# root-owned ./exports on Linux hosts.
as_of=$(date -u +%F)
docker compose exec -T api python manage.py export_analytics --as-of "$as_of" --out /tmp/exports ||
  fail "export_analytics"
rm -rf "exports/as_of=$as_of" && mkdir -p exports
docker compose cp "api:/tmp/exports/as_of=$as_of" exports/ >/dev/null || fail "copy the export out"
for file in request_events.parquet request_lifecycle.parquet daily_throughput.parquet _run.json; do
  [ -s "exports/as_of=$as_of/$file" ] || fail "exports/as_of=$as_of/$file is missing on the host"
done
echo "ok export"
