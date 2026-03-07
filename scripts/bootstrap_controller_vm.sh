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

echo "[INFO] Pinning controller packaging toolchain..."
python -m pip install --upgrade 'pip==24.3.1'
python -m pip uninstall -y setuptools packaging wheel pbr >/dev/null 2>&1 || true
python -m pip install   'setuptools==68.2.2'   'wheel==0.45.1'   'packaging==24.2'   'pbr==6.1.1'
python scripts/check_build_toolchain.py

python -m pip install -r vm-a1-controller/requirements-controller.txt
bash scripts/install_ryu_patched.sh .venv-controller
python scripts/check_build_toolchain.py
python scripts/check_controller_env.py
chmod +x vm-a1-controller/run_controller.sh

echo "[OK] Controller environment ready."
find "$ROOT_DIR" -type f -name "*.sh" -exec chmod +x {} +
