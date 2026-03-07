#!/usr/bin/env bash
set -euo pipefail

# Hybrid SDN Load Balancer - Controller VM launcher
#
# Optional env vars:
#   CONFIG     Path to YAML config (default ./config.controller.yaml)
#   OFP_PORT   OpenFlow listen port (default 6633)
#   REST_PORT  REST API port (default read from config or 8080)
#
# Example:
#   CONFIG=./config.controller.yaml OFP_PORT=6633 REST_PORT=8080 ./run_controller.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${CONFIG:-$SCRIPT_DIR/config.controller.yaml}"
OFP_PORT="${OFP_PORT:-6633}"

# Read REST port from config if possible
REST_PORT_DEFAULT="$(python3 - <<'PY'
import os, yaml
cfg_path=os.environ.get('CONFIG','./config.controller.yaml')
try:
    with open(cfg_path,'r',encoding='utf-8') as f:
        cfg=yaml.safe_load(f) or {}
    print(int((cfg.get('controller') or {}).get('rest_api_port',8080)))
except Exception:
    print(8080)
PY
)"
REST_PORT="${REST_PORT:-$REST_PORT_DEFAULT}"

export SDN_HYBRID_LB_CONFIG="$CONFIG"

echo "[Controller] Using config: $SDN_HYBRID_LB_CONFIG"
echo "[Controller] OpenFlow listen port: $OFP_PORT"
echo "[Controller] REST API port: $REST_PORT"

# Notes:
# - OpenFlow TCP listen port: used by OVS/Mininet to connect to the controller
# - wsapi port: used for the optional REST API (status/recompute/health)

cd "$SCRIPT_DIR"

if ! command -v ryu-manager >/dev/null 2>&1; then
  echo "[ERROR] ryu-manager not found. Run: bash ../scripts/bootstrap_controller_vm.sh" >&2
  exit 1
fi

ryu-manager \
  --ofp-tcp-listen-port "$OFP_PORT" \
  --wsapi-port "$REST_PORT" \
  sdn_hybrid_lb/controller/ryu_app.py
