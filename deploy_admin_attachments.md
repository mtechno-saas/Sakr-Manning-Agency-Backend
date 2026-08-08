# Deploy admin-attachments endpoint to production

## What was pushed
- Commit `bc70539d` on `mtechno-saas/Sakr-Manning-Agency-Backend` branch `server-updates`
- 3 files, +228/-1 lines
- New endpoint: `GET/POST /api/contracts/{id}/admin-attachments/`
- New field: `admin_attachments` on every contract detail payload

## Run on production (root@srv1080138)

```bash
cd /opt/sakr/Sakr-Manning-Agency-Backend-New
git pull origin server-updates
source venv/bin/activate  # or .venv/bin/activate
python manage.py migrate --noinput
supervisorctl restart sakr   # or: systemctl restart sakr-gunicorn  /  pkill -HUP -f gunicorn
```

## Verify (paste into Django shell on production)

```python
from api.models import Contract
from api.serializer import ContractSerializer
c = Contract.objects.exclude(user__isnull=True).order_by('-id').first()
data = ContractSerializer(c).data
print('contract_id =', c.id)
print('admin_attachments =', data['admin_attachments'])
print('count =', len(data['admin_attachments']))
```

Then via API:
```bash
curl -H "Authorization: Bearer $TOKEN" \
     https://backend.sakrshipping.com/api/contracts/<id>/admin-attachments/
```

## If the previous venv path is different
The `source venv/bin/activate` line has 3 fallbacks (venv, .venv, none). If the
project uses a different venv path, run `ls -la | grep venv` first.

## What did NOT change
- No new migration (0068 already applied in the prior deploy)
- No frontend change (still hits /api/documents/ — that's option B we deferred)
