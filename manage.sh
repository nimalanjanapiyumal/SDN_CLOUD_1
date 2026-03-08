#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="$ROOT/logs"
mkdir -p "$LOGDIR"
ACTION="${1:-}"; SUB="${2:-}"
fix_perms(){ bash "$ROOT/scripts/fix_permissions.sh"; }
cleanup_ports(){ for p in 6633 8080; do if command -v lsof >/dev/null 2>&1; then lsof -ti tcp:"$p" | xargs -r kill -9 || true; else fuser -k "${p}/tcp" 2>/dev/null || true; fi; done; }
start_bg(){ local name="$1" cmd="$2" pidfile="$LOGDIR/${name}.pid" logfile="$LOGDIR/${name}.log"; nohup bash -lc "$cmd" >"$logfile" 2>&1 & echo $! > "$pidfile"; sleep 3; if kill -0 $(cat "$pidfile") 2>/dev/null; then echo "[OK] Started $name (PID $(cat "$pidfile"))"; echo "[LOG] tail -f $logfile"; else echo "[ERROR] $name failed to stay running. Last log lines:"; tail -n 60 "$logfile" || true; exit 1; fi; }
stop_bg(){ local name="$1" pidfile="$LOGDIR/${name}.pid"; if [[ -f "$pidfile" ]]; then kill $(cat "$pidfile") 2>/dev/null || true; rm -f "$pidfile"; fi; }
status_bg(){ local name="$1" pidfile="$LOGDIR/${name}.pid"; if [[ -f "$pidfile" ]] && kill -0 $(cat "$pidfile") 2>/dev/null; then echo "[INFO] $name running (PID $(cat "$pidfile"))"; else echo "[INFO] $name not running"; fi; }
logs_bg(){ local name="$1"; tail -n 80 "$LOGDIR/${name}.log"; }
case "$ACTION" in
  fix-perms) fix_perms ;;
  controller)
    case "$SUB" in
      bootstrap) fix_perms; bash "$ROOT/scripts/bootstrap_controller_vm.sh" ;;
      start) fix_perms; cleanup_ports; source "$ROOT/.venv-controller/bin/activate"; python "$ROOT/scripts/check_controller_env.py"; start_bg controller "cd '$ROOT/vm-a1-controller' && source '$ROOT/.venv-controller/bin/activate' && bash ./run_controller.sh" ;;
      stop) stop_bg controller ;;
      status) status_bg controller ;;
      logs) logs_bg controller ;;
      diag) bash "$ROOT/scripts/check_connectivity.sh" controller ;;
      *) echo 'usage: bash manage.sh controller {bootstrap|start|stop|status|logs|diag}' ; exit 1 ;;
    esac ;;
  dashboard)
    case "$SUB" in
      bootstrap) fix_perms; bash "$ROOT/scripts/bootstrap_dashboard_vm.sh" ;;
      start) fix_perms; start_bg dashboard "cd '$ROOT/dashboard/flask_dashboard' && source '$ROOT/.venv-dashboard/bin/activate' && python app.py" ;;
      stop) stop_bg dashboard ;;
      status) status_bg dashboard ;;
      logs) logs_bg dashboard ;;
      *) echo 'usage: bash manage.sh dashboard {bootstrap|start|stop|status|logs}' ; exit 1 ;;
    esac ;;
  dataplane)
    case "$SUB" in
      bootstrap) fix_perms; bash "$ROOT/scripts/bootstrap_dataplane_vm.sh" ;;
      start) fix_perms; cd "$ROOT/vm-a2-dataplane"; exec bash ./run_mininet.sh ;;
      diag) bash "$ROOT/scripts/check_connectivity.sh" dataplane ;;
      *) echo 'usage: CTRL_IP=<ip> bash manage.sh dataplane {bootstrap|start|diag}' ; exit 1 ;;
    esac ;;
  *) echo 'usage: bash manage.sh {fix-perms|controller|dashboard|dataplane} ...'; exit 1 ;;
esac
