#!/usr/bin/env bash
set -euo pipefail

CONFIG="${CONFIG:-./config.controller.yaml}"
OFP_PORT="${OFP_PORT:-6633}"

REST_PORT_DEFAULT="$(python - <<'PY'
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
export EVENTLET_NO_GREENDNS=yes
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"

echo "[Controller] Using config: $SDN_HYBRID_LB_CONFIG"
echo "[Controller] OpenFlow listen port: $OFP_PORT"
echo "[Controller] REST API port: $REST_PORT"

controller_python="${PYTHON:-python}"
"$controller_python" -m os_ken.cmd.manager \
  --ofp-tcp-listen-port "$OFP_PORT" \
  --wsapi-port "$REST_PORT" \
  sdn_hybrid_lb/controller/osken_app.py
