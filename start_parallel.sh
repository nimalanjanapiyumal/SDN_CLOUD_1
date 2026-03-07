#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"
bash manage.sh stack bootstrap
bash manage.sh stack start
echo "[OK] Controller + dashboard started on this host."
echo "[INFO] Controller logs: bash manage.sh controller logs"
echo "[INFO] Dashboard logs:  bash manage.sh dashboard logs"
