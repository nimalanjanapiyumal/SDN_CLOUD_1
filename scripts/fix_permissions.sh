#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
find "$ROOT" -type f \( -name '*.sh' -o -name '*.py' \) -exec chmod +x {} +
echo "[OK] Shell script permissions repaired under: $ROOT"
