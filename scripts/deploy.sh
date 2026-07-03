#!/bin/bash
# Mystral deploy script
# Usage: ./scripts/deploy.sh

set -euo pipefail

PROJECT_DIR="/var/www/mystral"
COMPOSE="docker compose -f docker-compose.prod.yml"

cd "$PROJECT_DIR"

echo "[$(date)] Pulling latest code..."
git pull origin main

echo "[$(date)] Stopping containers..."
$COMPOSE down --remove-orphans

echo "[$(date)] Building and starting..."
$COMPOSE up --build -d

echo "[$(date)] Done. Container status:"
$COMPOSE ps
