#!/bin/bash
set -e

PORT="${PORT:-8000}"
echo "Starting Vera Bot on port $PORT..."
exec uvicorn bot:app --host 0.0.0.0 --port "$PORT"
