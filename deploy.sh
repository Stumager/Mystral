#!/bin/bash
set -e

echo "→ Pulling latest..."
git pull origin main

echo "→ Building..."
docker-compose -f docker-compose.prod.yml build

echo "→ Restarting..."
docker-compose -f docker-compose.prod.yml up -d

echo "✓ Mystral deployed"
