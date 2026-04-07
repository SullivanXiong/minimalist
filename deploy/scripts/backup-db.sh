#!/usr/bin/env bash
# Database backup with 30-day retention
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/minimalist_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "Backing up database to ${BACKUP_FILE}..."
docker compose exec -T postgres pg_dump \
    -U minimalist \
    -d minimalist \
    --no-owner \
    --no-privileges \
    | gzip > "$BACKUP_FILE"

echo "Backup complete: $(du -h "$BACKUP_FILE" | cut -f1)"

# Remove backups older than retention period
echo "Removing backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR" -name "minimalist_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

echo "Current backups:"
ls -lh "$BACKUP_DIR"/minimalist_*.sql.gz 2>/dev/null || echo "  (none)"
