#!/usr/bin/env bash
set -e

echo "run migration"

python manage.py migrate --noinput

exec "$@"
