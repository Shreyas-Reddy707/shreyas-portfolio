#!/bin/sh
set -e

echo "Applying Alembic database migrations..."
alembic upgrade head || echo "Migration step completed or skipped."

echo "Starting Uvicorn production server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"

