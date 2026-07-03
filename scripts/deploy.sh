#!/bin/bash
# Mystral deploy script
# Usage: ./scripts/deploy.sh

set -euo pipefail

cd /var/www/mystral \
  && git pull origin main \
  && docker compose -f docker-compose.prod.yml down --remove-orphans \
  && docker compose -f docker-compose.prod.yml up --build -d \
  && for f in frontend/public/tarot/*.jpg; do git show "HEAD:$f" > "$f"; done \
  && docker compose -f docker-compose.prod.yml restart frontend
