#!/bin/bash
# Confirm the post() fix is live: POST to detail URL should return 400
# with the new error text, NOT 500 TypeError.

set -e
cd /opt/sakr/Sakr-Manning-Agency-Backend-New

echo "=== Show current commit ==="
git log -1 --oneline

echo ""
echo "=== Force restart gunicorn (HUP doesn't reload Python code) ==="
# Find gunicorn master and TERM it gracefully; supervisor/systemd would normally do this,
# but we can also kill it directly and let nohup respawn it.
pkill -TERM -f "gunicorn.*saker.wsgi" || true
sleep 3

# Start a fresh gunicorn. Adjust the bind/workers to match the production setup.
nohup /opt/sakr/Sakr-Manning-Agency-Backend-New/venv/bin/gunicorn \
  saker.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 3 \
  --timeout 120 \
  --access-logfile /var/log/gunicorn/access.log \
  --error-logfile /var/log/gunicorn/error.log \
  > /var/log/gunicorn/stdout.log 2>&1 &
sleep 4

echo "=== Confirm new gunicorn is up ==="
ps aux | grep -E "gunicorn.*saker" | grep -v grep | awk '{print $2, $9, $11, $12, $13}'

echo ""
echo "=== Test 1: hit detail URL with POST (no auth) -> 401, not 500 ==="
# No auth at all -> should be 401. If you see 500, the old code is still running.
curl -s -o /tmp/exp_resp.html -w "HTTP %{http_code}\n" \
  -X POST "https://backend.sakrshipping.com/api/expiring-documents/user_42_passport_expiry_date/"

echo ""
echo "=== Test 2: GET works (no auth) -> 401 ==="
curl -s -o /dev/null -w "HTTP %{http_code}\n" \
  "https://backend.sakrshipping.com/api/expiring-documents/"

echo ""
echo "=== Test 3: test with auth (replace PASSWORD) ==="
TOKEN=$(curl -s -X POST https://backend.sakrshipping.com/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"morad@gmail.com","password":"REPLACE_ME"}' \
  | python -c "import sys,json; print(json.load(sys.stdin).get('access',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "Login failed. Edit this script and put a real password in, then re-run."
  exit 0
fi

# Create a tiny dummy file to upload
echo "fake pdf" > /tmp/test_visa.pdf

echo "POST to detail URL (with auth) -> expect 400:"
curl -s -w "\nHTTP %{http_code}\n" \
  -X POST "https://backend.sakrshipping.com/api/expiring-documents/user_42_passport_expiry_date/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "document_type=Passport" \
  -F "expiry_date=2027-01-01" \
  -F "user=42" \
  -F "file=@/tmp/test_visa.pdf"

echo ""
echo "POST to base URL (with auth) -> expect 201:"
curl -s -w "\nHTTP %{http_code}\n" \
  -X POST "https://backend.sakrshipping.com/api/expiring-documents/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "document_type=Passport" \
  -F "expiry_date=2027-01-01" \
  -F "user=42" \
  -F "file=@/tmp/test_visa.pdf"
