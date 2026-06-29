#!/bin/bash
# Mystral backup script — PostgreSQL + .env.prod
# Run daily via cron: 0 4 * * * /var/www/mystral/scripts/backup.sh

set -euo pipefail

PROJECT_DIR="/var/www/mystral"
BACKUP_DIR="/var/www/backups/mystral"
KEEP_DAYS=14
DATE=$(date +%Y-%m-%d_%H-%M)

mkdir -p "$BACKUP_DIR"

# 1. PostgreSQL dump
echo "[$(date)] Starting PostgreSQL backup..."
docker exec mystral-postgres-1 pg_dump -U mystral mystral | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"
echo "[$(date)] DB backup: $BACKUP_DIR/db_$DATE.sql.gz ($(du -h "$BACKUP_DIR/db_$DATE.sql.gz" | cut -f1))"

# 2. .env.prod (credentials)
if [ -f "$PROJECT_DIR/.env.prod" ]; then
  cp "$PROJECT_DIR/.env.prod" "$BACKUP_DIR/env_$DATE.bak"
  echo "[$(date)] .env.prod backed up"
fi

# 3. Cleanup old backups
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +$KEEP_DAYS -delete
find "$BACKUP_DIR" -name "env_*.bak" -mtime +$KEEP_DAYS -delete
echo "[$(date)] Cleaned backups older than $KEEP_DAYS days"

# 4. Summary
echo "[$(date)] Backup complete. Current backups:"
ls -lh "$BACKUP_DIR"
