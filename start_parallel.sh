#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
bash "$ROOT/manage.sh" fix-perms
bash "$ROOT/manage.sh" controller bootstrap
bash "$ROOT/manage.sh" dashboard bootstrap
bash "$ROOT/manage.sh" controller start
export CONTROLLER_API_URL="${CONTROLLER_API_URL:-http://127.0.0.1:8080}"
bash "$ROOT/manage.sh" dashboard start
