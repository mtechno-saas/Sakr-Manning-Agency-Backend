# Paste this whole block into the production shell.
# (Lines starting with # are comments — safe to include.)

set -e
cd /opt/sakr/Sakr-Manning-Agency-Backend-New

echo "=== Commit BEFORE ==="
git log -1 --oneline

echo "=== Pulling ==="
git pull origin server-updates

echo "=== Commit AFTER ==="
git log -1 --oneline

echo "=== Activating venv ==="
source venv/bin/activate

echo "=== Migrate (no-op if 0068 already applied) ==="
python manage.py migrate --noinput

echo "=== Restarting gunicorn ==="
supervisorctl restart sakr 2>/dev/null \
  || supervisorctl restart gunicorn 2>/dev/null \
  || pkill -HUP -f gunicorn || true

echo "=== Show new URL patterns for admin-attachments ==="
python manage.py shell -c "
from rest_framework.routers import DefaultRouter
from api.views import ContractViewSet
r = DefaultRouter()
r.register(r'contracts', ContractViewSet, basename='contract')
for p in r.urls:
    if 'attachment' in str(p.pattern):
        print(p.pattern, '->', p.name)
"

echo "=== Done. Now test from your browser: ==="
echo "    GET https://backend.sakrshipping.com/api/contracts/56/admin-attachments/"
echo "    GET https://backend.sakrshipping.com/api/contracts/56/admin-attachments/67/"
