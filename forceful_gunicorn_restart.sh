# Forceful gunicorn restart - actual code reload
# Run on production: root@srv1080138

# Show what's currently running
echo "=== Current gunicorn processes ==="
ps aux | grep -E "gunicorn|sakr" | grep -v grep | head -10

echo "=== Force kill all gunicorn workers ==="
pkill -9 -f gunicorn 2>/dev/null || true
sleep 2

echo "=== Verify nothing is running ==="
ps aux | grep -E "gunicorn|sakr" | grep -v grep | head -5

echo "=== Start gunicorn fresh ==="
# Try common startup methods in order
supervisorctl start sakr 2>/dev/null \
  || supervisorctl start gunicorn 2>/dev/null \
  || systemctl start gunicorn 2>/dev/null \
  || systemctl start sakr-gunicorn 2>/dev/null \
  || (cd /opt/sakr/Sakr-Manning-Agency-Backend-New && nohup gunicorn saker.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 > /var/log/sakr-gunicorn.log 2>&1 &)

sleep 3

echo "=== New gunicorn processes ==="
ps aux | grep -E "gunicorn|sakr" | grep -v grep | head -10

echo "=== Test the new endpoint via curl ==="
# Login
TOKEN=$(curl -s -X POST https://backend.sakrshipping.com/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"morad@gmail.com","password":"YOUR_PASSWORD"}' \
  | python -c "import sys, json; print(json.load(sys.stdin).get('access',''))" 2>/dev/null)

if [ -n "$TOKEN" ]; then
  echo "Got token, testing..."
  curl -s -o /dev/null -w "List status: %{http_code}\n" \
    -H "Authorization: Bearer $TOKEN" \
    "https://backend.sakrshipping.com/api/contracts/56/admin-attachments/"
  curl -s -o /dev/null -w "Detail status: %{http_code}\n" \
    -H "Authorization: Bearer $TOKEN" \
    "https://backend.sakrshipping.com/api/contracts/56/admin-attachments/67/"
else
  echo "Login failed, can't test from server. Test from your browser."
fi
