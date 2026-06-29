#!/bin/bash
# Mystral restore script
# Usage: ./scripts/restore.sh /var/www/backups/mystral/db_2026-06-30_04-00.sql.gz

set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <backup_file.sql.gz>"
  echo ""
  echo "Available backups:"
  ls -lh /var/www/backups/mystral/db_*.sql.gz 2>/dev/null || echo "  No backups found"
  exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Error: File not found: $BACKUP_FILE"
  exit 1
fi

echo "WARNING: This will overwrite the current database!"
echo "Backup: $BACKUP_FILE"
read -p "Continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

echo "[$(date)] Restoring from $BACKUP_FILE..."

# Drop and recreate
docker exec mystral-postgres-1 psql -U mystral -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='mystral' AND pid <> pg_backend_pid();" postgres 2>/dev/null || true
docker exec mystral-postgres-1 dropdb -U mystral mystral 2>/dev/null || true
docker exec mystral-postgres-1 createdb -U mystral mystral

# Restore
gunzip -c "$BACKUP_FILE" | docker exec -i mystral-postgres-1 psql -U mystral mystral

echo "[$(date)] Restore complete. Restarting backend..."
cd /var/www/mystral
docker compose -f docker-compose.prod.yml restart backend bot

echo "[$(date)] Done."
