#!/bin/bash
# SOCForge — PostgreSQL Backup Script
# Usage: ./scripts/backup_db.sh
# Cron:  0 2 * * * /path/to/socforge/scripts/backup_db.sh

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/socforge_${TIMESTAMP}.sql.gz"

# Load env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

DB_HOST="${PGHOST:-localhost}"
DB_PORT="${PGPORT:-5432}"
DB_NAME="${POSTGRES_DB:-socforge}"
DB_USER="${POSTGRES_USER:-socforge_admin}"

echo "=== SOCForge Database Backup ==="
echo "Target: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
echo "Output: ${BACKUP_FILE}"

mkdir -p "$BACKUP_DIR"

# Run backup
PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --format=custom \
    --compress=9 \
    --verbose \
    2>&1 | gzip > "$BACKUP_FILE"

FILESIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "Backup complete: ${BACKUP_FILE} (${FILESIZE})"

# Cleanup old backups
echo "Cleaning backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR" -name "socforge_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete
REMAINING=$(ls -1 "$BACKUP_DIR"/socforge_*.sql.gz 2>/dev/null | wc -l)
echo "Remaining backups: ${REMAINING}"
echo "=== Backup Complete ==="
