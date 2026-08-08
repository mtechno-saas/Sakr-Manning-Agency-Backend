#!/bin/bash
# Verification: log in, find a contract, hit the new endpoint
# Run on production: root@srv1080138

set -e
cd /opt/sakr/Sakr-Manning-Agency-Backend-New
source venv/bin/activate 2>/dev/null || source .venv/bin/activate

python manage.py shell <<'PY'
import requests

# Log in
r = requests.post("https://backend.sakrshipping.com/api/login/", {
    "email": "morad@gmail.com",      # <-- replace with a real admin email
    "password": "your_password",     # <-- replace
})
print("Login status:", r.status_code)
token = r.json().get("access")
headers = {"Authorization": f"Bearer {token}"}

# Find a contract id and an admin attachment id
r = requests.get("https://backend.sakrshipping.com/api/contracts/56/", headers=headers)
print("Contract 56 status:", r.status_code)
print("admin_attachments field present:", "admin_attachments" in r.json() if r.status_code == 200 else r.text[:200])

# Try the new endpoints
r = requests.get("https://backend.sakrshipping.com/api/contracts/56/admin-attachments/", headers=headers)
print("List endpoint status:", r.status_code)
if r.status_code == 200:
    aids = [a["id"] for a in r.json()]
    print("Found attachment IDs:", aids)
    if aids:
        r2 = requests.get(f"https://backend.sakrshipping.com/api/contracts/56/admin-attachments/{aids[0]}/", headers=headers)
        print("Detail endpoint status:", r2.status_code)
        print("Detail response keys:", list(r2.json().keys()) if r2.status_code == 200 else r2.text[:200])
PY
