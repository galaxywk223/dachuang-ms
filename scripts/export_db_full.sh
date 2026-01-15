#!/usr/bin/env bash
set -euo pipefail

# Defaults align with backend/config/settings.py
DB_NAME="${DB_NAME:-dachuang_db}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-123456}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_FILE="${OUTPUT_FILE:-$SCRIPT_DIR/../dachuang_db_full.sql}"

if ! command -v pg_dump >/dev/null 2>&1; then
  echo "pg_dump is not available in PATH." >&2
  exit 1
fi

OUTPUT_DIR="$(dirname "$OUTPUT_FILE")"
mkdir -p "$OUTPUT_DIR"

export PGPASSWORD="$DB_PASSWORD"
pg_dump \
  --host "$DB_HOST" \
  --port "$DB_PORT" \
  --username "$DB_USER" \
  --format=plain \
  --file "$OUTPUT_FILE" \
  "$DB_NAME"
unset PGPASSWORD

echo "Exported database to $OUTPUT_FILE"
