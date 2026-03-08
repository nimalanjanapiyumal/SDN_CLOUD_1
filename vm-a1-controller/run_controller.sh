#!/usr/bin/env bash
set -euo pipefail
CONFIG="${CONFIG:-./config.controller.yaml}"
OFP_PORT="${OFP_PORT:-6633}"
REST_PORT="${REST_PORT:-8080}"
export SDN_HYBRID_LB_CONFIG="$CONFIG"
export OFP_PORT REST_PORT

echo "[Controller] Using config: $SDN_HYBRID_LB_CONFIG"
echo "[Controller] OpenFlow listen port: $OFP_PORT"
echo "[Controller] REST API port: $REST_PORT"
exec python3 ./launch_ryu_compat.py
