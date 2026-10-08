# Deploy the M/V cleanup + no-expiry report commands to the new server.
# Paste this whole block into the Hostinger hPanel browser terminal
# at https://hpanel.hostinger.com (root@srv2032989.hstgr.cloud).
#
# Pre-flight:
#   - Make sure your local branch is pushed:
#       git push origin server-updates
#   - Make sure your working tree is clean.
#
# After running, gunicorn picks up the new commands. They are
# available as:
#     python manage.py cleanup_sea_service_mv
#     python manage.py report_health_cert_no_expiry_candidates

set -e
cd /opt/sakr/Sakr-Manning-Agency-Backend

echo "=== Remotes ==="
git remote -v

echo "=== Commit BEFORE ==="
git log -1 --oneline

echo "=== Pulling server-updates ==="
git pull origin server-updates

echo "=== Commit AFTER ==="
git log -1 --oneline

echo "=== Activating venv ==="
source venv/bin/activate

echo "=== Migrate (no-op if 0076 already applied) ==="
python manage.py migrate --noinput

echo "=== Verifying new commands are importable ==="
python manage.py help cleanup_sea_service_mv 2>&1 | head -5
echo "---"
python manage.py help report_health_cert_no_expiry_candidates 2>&1 | head -5

echo "=== Restarting gunicorn ==="
# New server uses systemd (sakr-backend.service), not supervisor.
sudo systemctl restart sakr-backend

echo "=== Service status ==="
sudo systemctl status sakr-backend --no-pager | head -10

echo "=== Smoke test ==="
curl -sS -o /dev/null -w "HTTP %{http_code}  %{size_download} bytes\n" \
    https://backend.sakrshipping.com/api/ships/?name=Octavies+1

echo "=== Done. You can now run the cleanup commands. ==="
echo ""
echo "Preview the M/V cleanup (no DB changes):"
echo "    python manage.py cleanup_sea_service_mv --dry-run"
echo ""
echo "Apply the M/V cleanup:"
echo "    python manage.py cleanup_sea_service_mv"
echo ""
echo "List no-expiry cert candidates for manual review:"
echo "    python manage.py report_health_cert_no_expiry_candidates"
echo ""
echo "Write the candidate report to a JSON file:"
echo "    python manage.py report_health_cert_no_expiry_candidates --report /tmp/no_expiry.json"