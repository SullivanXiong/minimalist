#!/usr/bin/env bash
# Restore database from backup
set -euo pipefail

BACKUP_FILE="${1:?Usage: restore-db.sh <backup-file>}"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "WARNING: This will overwrite the current database!"
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo "Restoring from ${BACKUP_FILE}..."
gunzip -c "$BACKUP_FILE" | docker compose exec -T postgres psql \
    -U minimalist \
    -d minimalist

echo "Restore complete."
