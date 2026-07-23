#!/usr/bin/env bash
# Container entrypoint: bootstrap the app so `docker compose up` is enough to use it.
#   1. collect static files
#   2. migrate database
#   3. download media assets (if missing)
#   4. seed sample data (only on first boot)
#   5. create a default superuser (if env provided)
#   6. launch gunicorn

set -u

echo "==> [1/6] Collecting static files"
python manage.py collectstatic --noinput

echo "==> [2/6] Running database migrations"
python manage.py migrate --noinput

echo "==> [3/6] Ensuring media assets"
python manage.py ensure_media

echo "==> [4/6] Seeding sample data (first boot only)"
python manage.py shell -c \
  "from apps.core.models import Category; print('HAS_DATA' if Category.objects.exists() else 'NO_DATA')" \
  | grep -q NO_DATA \
  && python manage.py seed_data \
  || echo "    Data already present, skipping seed_data."

echo "==> [5/6] Ensuring default superuser"
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

echo "==> [6/6] Starting gunicorn"
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --threads 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
