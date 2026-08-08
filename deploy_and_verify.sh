#!/bin/bash
# Full deploy of admin-attachments endpoint + verification
# Run on production: root@srv1080138

set -e
cd /opt/sakr/Sakr-Manning-Agency-Backend-New

echo "=== Current commit (before) ==="
git log -1 --oneline

echo "=== Pulling ==="
git pull origin server-updates

echo "=== Current commit (after) ==="
git log -1 --oneline

echo "=== Activating venv ==="
if [ -d venv ]; then source venv/bin/activate
elif [ -d .venv ]; then source .venv/bin/activate
fi

echo "=== Migrate (no-op if already on 0068) ==="
python manage.py migrate --noinput

echo "=== Restarting gunicorn ==="
if command -v supervisorctl >/dev/null 2>&1; then
    supervisorctl restart sakr || supervisorctl restart gunicorn || true
elif systemctl list-units --type=service 2>/dev/null | grep -q gunicorn; then
    systemctl restart gunicorn
else
    pkill -HUP -f gunicorn || true
fi

echo "=== Smoke test: show URL patterns for contracts/ ==="
python manage.py shell -c "
from django.urls import get_resolver
from rest_framework.routers import DefaultRouter
from api.views import ContractViewSet

r = DefaultRouter()
r.register(r'contracts', ContractViewSet, basename='contract')
print('Registered URL patterns:')
for p in r.urls:
    if 'attachment' in str(p.pattern):
        print(' ', p.pattern, '->', p.name)
"
