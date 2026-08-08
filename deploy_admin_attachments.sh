#!/bin/bash
# Deploy the new admin-attachments endpoint to production
# Run on production: root@srv1080138

set -e
cd /opt/sakr/Sakr-Manning-Agency-Backend-New

echo "=== Pulling latest ==="
git pull origin server-updates

echo "=== Activating venv ==="
source venv/bin/activate 2>/dev/null || source .venv/bin/activate || true

echo "=== Migrating (0068 already applied last deploy, but no-op is safe) ==="
python manage.py migrate --noinput

echo "=== Restarting gunicorn ==="
supervisorctl restart sakr 2>/dev/null || systemctl restart sakr-gunicorn 2>/dev/null || pkill -HUP -f gunicorn

echo "=== Smoke test: pick a contract ID and check the new field ==="
python manage.py shell -c "
from api.models import Contract
from api.serializer import ContractSerializer
qs = Contract.objects.exclude(user__isnull=True).order_by('-id')[:3]
for c in qs:
    data = ContractSerializer(c).data
    print(f'Contract {c.id} user={c.user_id} admin_attachments_count={len(data[\"admin_attachments\"])}')
print('OK')
"

echo "=== Done ==="
