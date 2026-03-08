#!/usr/bin/env bash
set -euo pipefail
CTRL_IP="${CTRL_IP:-192.168.56.10}"
CTRL_PORT="${CTRL_PORT:-6633}"
SERVERS="${SERVERS:-3}"
CLEAN_MININET="${CLEAN_MININET:-1}"
echo "[Dataplane] Controller target: ${CTRL_IP}:${CTRL_PORT}"
python3 - <<PY
import socket
ip='${CTRL_IP}'; port=int('${CTRL_PORT}')
try:
    s=socket.create_connection((ip,port),timeout=2); s.close(); print('[Dataplane] Controller TCP port is reachable before Mininet start.')
except Exception as e:
    print(f'[Dataplane] WARNING: controller not reachable yet: {e}')
PY
if [[ "$CLEAN_MININET" == "1" ]]; then
  sudo pkill -f backend_server.py || true
  sudo pkill -f 'iperf3 -s -p 5201' || true
  sudo mn -c || true
  sudo ovs-vsctl --if-exists del-br s1 || true
fi
exec sudo -E python3 mininet/topo_lb.py --controller-ip "$CTRL_IP" --controller-port "$CTRL_PORT" --servers "$SERVERS"
