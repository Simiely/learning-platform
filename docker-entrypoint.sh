#!/usr/bin/env bash
# Container entrypoint: bootstrap the app so `docker compose up` is enough to use it.
#   1. collect static files
#   2. migrate database
#   3. download media assets (if missing)
#   4. seed sample data (only on first boot)
#   5. create a default superuser (if env provided)
#   6. launch gunicorn

set -eu

echo "==> [1/8] Collecting static files"
python manage.py collectstatic --noinput

echo "==> [2/8] Running database migrations"
# Host-mounted db/ may have wrong owner for the non-root 'app' user.
# Fix permissions before any DB write to avoid "readonly database" error.
chmod -R a+w /app/db/ 2>/dev/null || true
python manage.py migrate --noinput

echo "==> [3/8] Syncing media from bundled image copy"
# Volume mounts hide bundled media; keep a bundled copy so every deploy
# can sync updated images/audio without needing network download.
if [ -d /app/media-bundled ] && [ -n "$(ls -A /app/media-bundled)" ]; then
    rsync -ac /app/media-bundled/ /app/media/
    echo "    media synced (only changed files)."
else
    echo "    no bundled media found, using volume content as-is."
fi

echo "==> [4/8] Syncing seed data (creates new items, updates changed, never deletes)"
python manage.py seed_sync

echo "==> [5/8] Verifying data consistency (media files + data/ alignment)"
python manage.py check_data

echo "==> [6/8] Syncing image positions from seed_data"
# Non-fatal: sync_positions failure should NOT prevent gunicorn from starting.
# Wrap in set +e / set -e so we always reach gunicorn even if this step fails.
set +e
python manage.py sync_positions 2>&1
SYNC_EXIT=$?
set -e
if [ $SYNC_EXIT -ne 0 ]; then
    echo "    WARNING: sync_positions failed (exit $SYNC_EXIT), container will still start."
fi

echo "==> [7/8] Ensuring default superuser"
python manage.py shell -c "
import os
from django.contrib.auth.models import User
u = os.environ.get('DJANGO_SUPERUSER_USERNAME')
p = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
e = os.environ.get('DJANGO_SUPERUSER_EMAIL') or ''
if u and p and not User.objects.filter(username=u).exists():
    User.objects.create_superuser(u, e, p)
    print('    superuser created:', u)
else:
    print('    superuser already present or not configured, skipping.')
"

echo "==> [8/8] Starting gunicorn"
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --threads 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
