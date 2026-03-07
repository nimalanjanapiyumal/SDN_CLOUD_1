#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
bash "$ROOT_DIR/scripts/fix_permissions.sh"

sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-dev git curl build-essential gcc

if [[ ! -d .venv-controller ]]; then
  python3 -m venv .venv-controller
fi

source .venv-controller/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r vm-a1-controller/requirements-controller.txt
bash scripts/install_ryu_patched.sh .venv-controller
chmod +x vm-a1-controller/run_controller.sh

echo "[OK] Controller environment ready."
find "$ROOT_DIR" -type f -name "*.sh" -exec chmod +x {} +
