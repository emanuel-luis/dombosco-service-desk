#!/bin/sh
# Create .env from .env.example with a freshly generated SECRET_KEY (used by make demo and CI).
# Leaves an existing .env alone. Fails, without leaving a half-written .env, when no generator works.
set -eu

[ -f .env ] && exit 0

key=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))' 2>/dev/null ||
  python -c 'import secrets; print(secrets.token_urlsafe(50))' 2>/dev/null ||
  openssl rand -hex 32 2>/dev/null || true)
if [ "${#key}" -lt 32 ]; then
  echo "make-env: could not generate SECRET_KEY (needs python3, python or openssl)" >&2
  exit 1
fi

tmp=$(mktemp .env.XXXXXX)
sed "s|^SECRET_KEY=.*|SECRET_KEY=$key|" .env.example >"$tmp"
mv "$tmp" .env
echo "make-env: created .env with a generated SECRET_KEY"
