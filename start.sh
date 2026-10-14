#!/usr/bin/env bash
set -e

# Activate virtual environment if present
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Build frontend if dist doesn't exist yet and npm is available
if [ ! -d "frontend/dist" ] && command -v npm &> /dev/null; then
    echo "📦 Building Vue 3 frontend..."
    npm --prefix frontend install
    npm --prefix frontend run build
fi

# Launch application
python run.py
