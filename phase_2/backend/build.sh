#!/usr/bin/env bash
# Render Build Script for Phase 2 Backend

set -o errexit  # Exit on error

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Running database migrations..."
alembic upgrade head

echo "✅ Build completed successfully!"
