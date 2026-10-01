#!/usr/bin/env bash
# Serwer makiety do wystawienia publicznie (np. przez Cloudflare Tunnel).
# Użycie: PUBLIC_HOST=hydro.wnikiel.pl ./serve.sh
set -euo pipefail
cd "$(dirname "$0")"
export DEBUG=0
export SECRET_KEY="${SECRET_KEY:-$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')}"
: "${PUBLIC_HOST:?Ustaw PUBLIC_HOST, np. hydro.wnikiel.pl}"
uv sync -q
uv run python manage.py collectstatic --noinput -v 0
exec uv run gunicorn mockup.wsgi:application --bind 127.0.0.1:${PORT:-8100} --workers 2 --access-logfile -
