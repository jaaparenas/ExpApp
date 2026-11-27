#!/bin/sh
set -e

flask --app server db upgrade

exec gunicorn \
  --bind "0.0.0.0:${PORT:-5000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --access-logfile - \
  --error-logfile - \
  server:app
