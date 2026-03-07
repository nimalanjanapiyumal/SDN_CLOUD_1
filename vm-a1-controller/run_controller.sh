#!/usr/bin/env bash
set -euo pipefail

CONFIG="${CONFIG:-./config.controller.yaml}"
OFP_PORT="${OFP_PORT:-6633}"

# Auto-detect the project-level virtual environment created by scripts/bootstrap_controller_vm.sh
if [[ -x "../.venv-controller/bin/python" ]]; then
  export PATH="$(cd ../.venv-controller/bin && pwd):$PATH"
fi

REST_PORT_DEFAULT="$(python3 - <<'PY2'
import os, yaml
cfg_path=os.environ.get('CONFIG','./config.controller.yaml')
try:
    with open(cfg_path,'r',encoding='utf-8') as f:
        cfg=yaml.safe_load(f) or {}
    print(int((cfg.get('controller') or {}).get('rest_api_port',8080)))
except Exception:
    print(8080)
PY2
)"
REST_PORT="${REST_PORT:-$REST_PORT_DEFAULT}"

export SDN_HYBRID_LB_CONFIG="$CONFIG"

echo "[Controller] Using config: $SDN_HYBRID_LB_CONFIG"
echo "[Controller] OpenFlow listen port: $OFP_PORT"
echo "[Controller] REST API port: $REST_PORT"

action_bin="$(command -v ryu-manager || true)"
if [[ -z "$action_bin" ]]; then
  echo "ryu-manager not found. Run 'bash ../scripts/bootstrap_controller_vm.sh' first." >&2
  exit 1
fi

"$action_bin"   --ofp-tcp-listen-port "$OFP_PORT"   --wsapi-port "$REST_PORT"   sdn_hybrid_lb/controller/ryu_app.py
