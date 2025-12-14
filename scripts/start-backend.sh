#!/usr/bin/env bash
set -e

# Start the Django backend on 0.0.0.0:8000 using the existing venv.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/backend"

source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
