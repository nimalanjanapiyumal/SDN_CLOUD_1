#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG="${CONFIG:-$SCRIPT_DIR/config.controller.yaml}"
OFP_PORT="${OFP_PORT:-6633}"

if [[ -f "$ROOT_DIR/.venv-controller/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv-controller/bin/activate"
fi

REST_PORT_DEFAULT="$(CONFIG="$CONFIG" python - <<'PY'
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


python "$ROOT_DIR/scripts/check_controller_env.py"

echo "[Controller] Using config: $SDN_HYBRID_LB_CONFIG"
echo "[Controller] OpenFlow listen port: $OFP_PORT"
echo "[Controller] REST API port: $REST_PORT"

cd "$SCRIPT_DIR"

RYU_MANAGER="$ROOT_DIR/.venv-controller/bin/ryu-manager"
if [[ ! -x "$RYU_MANAGER" ]]; then
  RYU_MANAGER="$(command -v ryu-manager || true)"
fi

if [[ -z "$RYU_MANAGER" ]]; then
  echo "[ERROR] ryu-manager not found. Run: bash ../scripts/bootstrap_controller_vm.sh" >&2
  exit 1
fi

exec "$RYU_MANAGER" \
  --ofp-tcp-listen-port "$OFP_PORT" \
  --wsapi-port "$REST_PORT" \
  sdn_hybrid_lb/controller/ryu_app.py
