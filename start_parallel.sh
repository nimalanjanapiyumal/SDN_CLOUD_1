#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"
bash manage.sh stack bootstrap
bash manage.sh stack start
echo "[OK] Controller + dashboard started in parallel on this host."
echo "[INFO] Use: bash manage.sh controller logs"
echo "[INFO] Use: bash manage.sh dashboard logs"
