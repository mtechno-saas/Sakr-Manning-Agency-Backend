set -e
cd /opt/sakr/Sakr-Manning-Agency-Backend-New
echo "=== Remotes ===" && git remote -v
echo "=== Branches ===" && git branch -a | head -20
echo "=== Current commit ===" && git log -1 --oneline
echo "=== Pulling mtechno server-updates ===" && git pull mtechno server-updates
echo "=== New current commit ===" && git log -1 --oneline
echo "=== Activating venv ===" && source venv/bin/activate
echo "=== Migrate ===" && python manage.py migrate --noinput
echo "=== Restart gunicorn ===" && (supervisorctl restart sakr 2>/dev/null || supervisorctl restart gunicorn 2>/dev/null || pkill -HUP -f gunicorn)
echo "=== URL patterns for admin-attachments ==="
python manage.py shell -c "from rest_framework.routers import DefaultRouter
from api.views import ContractViewSet
r = DefaultRouter(); r.register(r'contracts', ContractViewSet, basename='contract')
for p in r.urls:
    if 'attachment' in str(p.pattern): print(p.pattern, '->', p.name)"
