
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTRL_IP="${CTRL_IP:-127.0.0.1}"
OFP_PORT="${OFP_PORT:-6633}"
cd "$SCRIPT_DIR"
sudo mn -c || true
sudo python3 mininet/topo_lb.py --controller-ip "$CTRL_IP" --controller-port "$OFP_PORT"
