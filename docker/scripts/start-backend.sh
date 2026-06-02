#!/bin/sh
set -eu

: "${DJANGO_WSGI:?DJANGO_WSGI is required}"
: "${PORT:?PORT is required}"

if [ "${STARTUP_DELAY:-0}" -gt 0 ]; then
  echo "Waiting ${STARTUP_DELAY}s before migration..."
  sleep "$STARTUP_DELAY"
fi

attempt=1
until python manage.py migrate --noinput --fake-initial; do
  if [ "$attempt" -ge 30 ]; then
    echo "Database migration failed after $attempt attempts" >&2
    exit 1
  fi
  echo "Database not ready for migration, retrying ($attempt/30)..." >&2
  attempt=$((attempt + 1))
  sleep 2
done

exec gunicorn "$DJANGO_WSGI" --bind "0.0.0.0:$PORT"
