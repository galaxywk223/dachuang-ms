#!/usr/bin/env bash
set -euo pipefail

# Start the Django backend on 0.0.0.0:8000, creating the venv and installing
# dependencies if they are missing.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
VENV_DIR="$BACKEND_DIR/venv"

cd "$BACKEND_DIR"

if [[ ! -d "$VENV_DIR" || ! -s "$VENV_DIR/bin/python" ]]; then
  # Clean up any broken venv contents before recreating.
  [[ -d "$VENV_DIR" ]] && rm -rf "$VENV_DIR"
  python3 -m venv "$VENV_DIR"
elif ! grep -qF "$VENV_DIR" "$VENV_DIR/bin/activate"; then
  # Recreate if the venv was moved (activate has a stale absolute path).
  rm -rf "$VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

if [[ ! -f "$VENV_DIR/.deps-installed" || "requirements.txt" -nt "$VENV_DIR/.deps-installed" ]]; then
  pip install -U pip
  pip install -r requirements.txt
  touch "$VENV_DIR/.deps-installed"
fi

SERVER_MODE="${DJANGO_SERVER_MODE:-gunicorn}"

if [[ "$SERVER_MODE" == "runserver" ]]; then
  exec python manage.py runserver 0.0.0.0:8000
else
  # Use a WSGI server to avoid Django's "development server" warning.
  # --reload keeps a similar dev experience (auto-reload on code changes).
  exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --reload
fi
