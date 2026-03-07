#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"
PID_DIR="$ROOT_DIR/run"
mkdir -p "$LOG_DIR" "$PID_DIR"

role="${1:-}"
action="${2:-}"

usage() {
  cat <<USAGE
Usage:
  bash manage.sh fix-perms
  bash manage.sh controller bootstrap|start|stop|restart|status
  bash manage.sh dashboard  bootstrap|start|stop|restart|status
  bash manage.sh dataplane  bootstrap|start|status

Examples:
  bash manage.sh fix-perms
  bash manage.sh controller bootstrap
  bash manage.sh controller start
  bash manage.sh dashboard bootstrap
  bash manage.sh dashboard start
  CTRL_IP=10.0.0.11 bash manage.sh dataplane bootstrap
  CTRL_IP=10.0.0.11 bash manage.sh dataplane start
USAGE
}

fix_perms() {
  bash "$ROOT_DIR/scripts/fix_permissions.sh"
}

start_bg() {
  local name="$1"
  local pidfile="$PID_DIR/${name}.pid"
  local logfile="$LOG_DIR/${name}.log"
  shift
  if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
    echo "[INFO] $name already running with PID $(cat "$pidfile")"
    exit 0
  fi
  nohup "$@" >"$logfile" 2>&1 &
  echo $! > "$pidfile"
  echo "[OK] Started $name (PID $!)"
  echo "[LOG] tail -f $logfile"
}

stop_bg() {
  local name="$1"
  local pidfile="$PID_DIR/${name}.pid"
  if [ ! -f "$pidfile" ]; then
    echo "[INFO] $name is not running"
    exit 0
  fi
  local pid
  pid="$(cat "$pidfile")"
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    echo "[OK] Stopped $name (PID $pid)"
  else
    echo "[INFO] $name PID file existed but process was not running"
  fi
  rm -f "$pidfile"
}

status_bg() {
  local name="$1"
  local pidfile="$PID_DIR/${name}.pid"
  if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
    echo "[OK] $name running with PID $(cat "$pidfile")"
  else
    echo "[INFO] $name not running"
  fi
}

controller_bootstrap() {
  bash "$ROOT_DIR/scripts/fix_permissions.sh"
  bash "$ROOT_DIR/scripts/bootstrap_controller_vm.sh"
}
controller_start() {
  bash "$ROOT_DIR/scripts/fix_permissions.sh"
  start_bg controller bash "$ROOT_DIR/vm-a1-controller/run_controller.sh"
}
controller_stop() { stop_bg controller; }
controller_status() { status_bg controller; }


dashboard_bootstrap() {
  bash "$ROOT_DIR/scripts/fix_permissions.sh"
  bash "$ROOT_DIR/scripts/bootstrap_dashboard_vm.sh"
}
dashboard_start() {
  bash "$ROOT_DIR/scripts/fix_permissions.sh"
  local cmd=(bash -lc "cd '$ROOT_DIR' && source .venv-dashboard/bin/activate && python dashboard/flask_dashboard/app.py")
  start_bg dashboard "${cmd[@]}"
}
dashboard_stop() { stop_bg dashboard; }
dashboard_status() { status_bg dashboard; }


dataplane_bootstrap() {
  bash "$ROOT_DIR/scripts/fix_permissions.sh"
  bash "$ROOT_DIR/scripts/bootstrap_dataplane_vm.sh"
}
dataplane_start() {
  bash "$ROOT_DIR/scripts/fix_permissions.sh"
  if [ -z "${CTRL_IP:-}" ]; then
    echo "[ERROR] Set CTRL_IP before starting dataplane, e.g. CTRL_IP=10.0.0.11 bash manage.sh dataplane start" >&2
    exit 1
  fi
  cd "$ROOT_DIR/vm-a2-dataplane"
  CTRL_IP="$CTRL_IP" bash ./run_mininet.sh
}
dataplane_status() {
  echo "[INFO] Dataplane runs interactively via Mininet; no background PID is tracked by default."
}

case "$role" in
  fix-perms)
    fix_perms
    ;;
  controller)
    case "$action" in
      bootstrap) controller_bootstrap ;;
      start) controller_start ;;
      stop) controller_stop ;;
      restart) controller_stop || true; controller_start ;;
      status) controller_status ;;
      *) usage; exit 1 ;;
    esac
    ;;
  dashboard)
    case "$action" in
      bootstrap) dashboard_bootstrap ;;
      start) dashboard_start ;;
      stop) dashboard_stop ;;
      restart) dashboard_stop || true; dashboard_start ;;
      status) dashboard_status ;;
      *) usage; exit 1 ;;
    esac
    ;;
  dataplane)
    case "$action" in
      bootstrap) dataplane_bootstrap ;;
      start) dataplane_start ;;
      status) dataplane_status ;;
      *) usage; exit 1 ;;
    esac
    ;;
  *)
    usage
    exit 1
    ;;
esac
