#!/usr/bin/env bash
# Deploy or update Minimalist
set -euo pipefail

ENV="${1:?Usage: deploy.sh <stage|prod>}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"

cd "$DEPLOY_DIR"

if [ "$ENV" = "stage" ]; then
    COMPOSE_FILES="-f docker-compose.base.yml -f docker-compose.stage.yml"
elif [ "$ENV" = "prod" ]; then
    COMPOSE_FILES="-f docker-compose.base.yml -f docker-compose.prod.yml"
else
    echo "Error: Unknown environment: $ENV (use 'stage' or 'prod')"
    exit 1
fi

echo "Deploying Minimalist ($ENV)..."

# Pull latest images
echo "Pulling images..."
docker compose $COMPOSE_FILES pull

# Run migrations
echo "Running migrations..."
docker compose $COMPOSE_FILES run --rm server python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
docker compose $COMPOSE_FILES run --rm server python manage.py collectstatic --noinput

# Restart services
echo "Restarting services..."
docker compose $COMPOSE_FILES up -d

echo "Deploy complete. Checking service health..."
sleep 5
docker compose $COMPOSE_FILES ps
