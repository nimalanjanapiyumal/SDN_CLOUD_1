
#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-dev git curl mininet openvswitch-switch iperf3
python3 -m venv .venv-dataplane
source .venv-dataplane/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r vm-a2-dataplane/requirements-dataplane.txt
chmod +x vm-a2-dataplane/run_mininet.sh

echo "[OK] Dataplane environment ready."
