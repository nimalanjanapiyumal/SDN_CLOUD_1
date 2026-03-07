
#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
bash "$ROOT_DIR/scripts/fix_permissions.sh"

sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-dev git curl build-essential
python3 -m venv .venv-dashboard
source .venv-dashboard/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r dashboard/requirements-dashboard.txt

echo "[OK] Dashboard environment ready."

find "$ROOT_DIR" -type f -name "*.sh" -exec chmod +x {} +
