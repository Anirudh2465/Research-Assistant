#!/bin/bash

echo "Starting Docker services..."
docker compose up -d

# Wait for services to be potentially ready (optional, but good practice if not relying solely on health checks)
# echo "Waiting for services to spin up..."
# sleep 5

echo "Starting FastAPI..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

echo "Starting Celery worker..."
celery -A backend.workers.celery_app worker --loglevel=info &

echo "Starting Celery Beat..."
celery -A backend.workers.celery_app beat --loglevel=info &

echo "Services started. Monitor logs for details."
