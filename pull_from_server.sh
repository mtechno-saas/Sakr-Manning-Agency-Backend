#!/bin/bash
set -e

# ============================================
# FILL IN YOUR SERVER DETAILS HERE
# ============================================
SERVER_USER="root"                          # SSH username
SERVER_IP="YOUR_SERVER_IP"                  # Server IP address
SERVER_PATH="/path/to/your/backend"         # Project path on server
SSH_KEY=""                                  # Optional: path to SSH key (e.g., ~/.ssh/id_rsa)
# ============================================

LOCAL_PROJECT="/run/media/storm/New Volume/2-TECHNO AQUARE"
BACKUP_NAME="server_backup_$(date +%Y%m%d_%H%M%S)"
ARCHIVE_NAME="${BACKUP_NAME}.tar.gz"

# Build SSH command
SSH_CMD="ssh"
SCP_CMD="scp"
if [ -n "$SSH_KEY" ]; then
    SSH_CMD="ssh -i $SSH_KEY"
    SCP_CMD="scp -i $SSH_KEY"
fi

echo "=========================================="
echo "  Pull Backend from Server to GitHub"
echo "=========================================="

# ----- Step 1: Create archive on server -----
echo ""
echo "[1/6] Creating archive on server..."
$SSH_CMD ${SERVER_USER}@${SERVER_IP} bash -c "'
cd ${SERVER_PATH}
tar czf /tmp/${ARCHIVE_NAME} \
    --exclude=venv \
    --exclude=.venv \
    --exclude=__pycache__ \
    --exclude=*.pyc \
    --exclude=.git \
    --exclude=media \
    --exclude=node_modules \
    .
echo \"Archive created: /tmp/${ARCHIVE_NAME}\"
ls -lh /tmp/${ARCHIVE_NAME}
'"

# ----- Step 2: Download archive -----
echo ""
echo "[2/6] Downloading archive from server..."
$SCP_CMD ${SERVER_USER}@${SERVER_IP}:/tmp/${ARCHIVE_NAME} "/tmp/${ARCHIVE_NAME}"
echo "Downloaded to /tmp/${ARCHIVE_NAME}"

# ----- Step 3: Local backup -----
echo ""
echo "[3/6] Creating local backup before overwriting..."
cd "$LOCAL_PROJECT"
mkdir -p "/tmp/local_backup_${BACKUP_NAME}"
cp -r .env db.sqlite3 saker/ "/tmp/local_backup_${BACKUP_NAME}/" 2>/dev/null || true
echo "Local backup saved to /tmp/local_backup_${BACKUP_NAME}/"

# ----- Step 4: Extract server files -----
echo ""
echo "[4/6] Extracting server files into local project..."
cd "$LOCAL_PROJECT"
tar xzf "/tmp/${ARCHIVE_NAME}" --overwrite
echo "Files extracted successfully"

# ----- Step 5: Update .gitignore to allow db, .env, settings -----
echo ""
echo "[5/6] Updating .gitignore to include db, .env, and settings..."

# Remove lines that ignore .env and db.sqlite3
sed -i '/^\.env$/d' .gitignore
sed -i '/^db\.sqlite3$/d' .gitignore
sed -i '/^\*\.sqlite3$/d' .gitignore

echo ""
echo "Updated .gitignore:"
cat .gitignore

# ----- Step 6: Commit and push to GitHub -----
echo ""
echo "[6/6] Committing and pushing to GitHub main..."
cd "$LOCAL_PROJECT"
git add -A
git status

echo ""
echo "=========================================="
echo "  Review the changes above."
echo "  If everything looks good, run:"
echo ""
echo "  git commit -m 'Pull latest backend from server (db + settings + env)'"
echo "  git push origin main"
echo ""
echo "=========================================="

# ----- Cleanup remote archive -----
echo ""
echo "Cleaning up server archive..."
$SSH_CMD ${SERVER_USER}@${SERVER_IP} "rm -f /tmp/${ARCHIVE_NAME}"
rm -f "/tmp/${ARCHIVE_NAME}"
echo "Done!"
