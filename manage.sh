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
  bash manage.sh controller bootstrap|start|stop|restart|status|logs
  bash manage.sh dashboard  bootstrap|start|stop|restart|status|logs
  bash manage.sh dataplane  bootstrap|start|status
  bash manage.sh stack      bootstrap|start|stop|restart|status
USAGE
}

fix_perms() { bash "$ROOT_DIR/scripts/fix_permissions.sh"; }

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
  local pid=$!
  echo "$pid" > "$pidfile"
  sleep 3
  if kill -0 "$pid" 2>/dev/null; then
    echo "[OK] Started $name (PID $pid)"
    echo "[LOG] tail -f $logfile"
  else
    echo "[ERROR] $name failed to stay running. Last log lines:"
    tail -n 40 "$logfile" || true
    rm -f "$pidfile"
    exit 1
  fi
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
    return 1
  fi
}

logs_bg() {
  local name="$1"
  tail -n 80 "$LOG_DIR/${name}.log"
}

controller_bootstrap() {
  bash "$ROOT_DIR/scripts/fix_permissions.sh"
  bash "$ROOT_DIR/scripts/bootstrap_controller_vm.sh"
}
controller_start() {
  bash "$ROOT_DIR/scripts/fix_permissions.sh"
  if [ ! -f "$ROOT_DIR/.venv-controller/bin/activate" ]; then
    echo "[ERROR] .venv-controller not found. Run: bash manage.sh controller bootstrap" >&2
    exit 1
  fi
  start_bg controller bash -lc "cd '$ROOT_DIR/vm-a1-controller' && source '$ROOT_DIR/.venv-controller/bin/activate' && python '$ROOT_DIR/scripts/check_controller_env.py' && bash ./run_controller.sh"
}
controller_stop() { stop_bg controller; }
controller_status() { status_bg controller; }
controller_logs() { logs_bg controller; }

dashboard_bootstrap() {
  bash "$ROOT_DIR/scripts/fix_permissions.sh"
  bash "$ROOT_DIR/scripts/bootstrap_dashboard_vm.sh"
}
dashboard_start() {
  bash "$ROOT_DIR/scripts/fix_permissions.sh"
  start_bg dashboard bash -lc "cd '$ROOT_DIR' && source '$ROOT_DIR/.venv-dashboard/bin/activate' && python dashboard/flask_dashboard/app.py"
}
dashboard_stop() { stop_bg dashboard; }
dashboard_status() { status_bg dashboard; }
dashboard_logs() { logs_bg dashboard; }

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

stack_bootstrap() {
  controller_bootstrap
  dashboard_bootstrap
}
stack_start() {
  controller_start
  dashboard_start
  stack_status
}
stack_stop() {
  dashboard_stop || true
  controller_stop || true
}
stack_restart() {
  stack_stop || true
  stack_start
}
stack_status() {
  controller_status || true
  dashboard_status || true
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
      logs) controller_logs ;;
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
      logs) dashboard_logs ;;
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
  stack)
    case "$action" in
      bootstrap) stack_bootstrap ;;
      start) stack_start ;;
      stop) stack_stop ;;
      restart) stack_restart ;;
      status) stack_status ;;
      *) usage; exit 1 ;;
    esac
    ;;
  *)
    usage
    exit 1
    ;;
esac
