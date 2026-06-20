#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
python "$BASE_DIR/manage.py" auto_archive_projects "$@"
