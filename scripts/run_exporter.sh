#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv-exporter
source .venv-exporter/bin/activate
pip install --upgrade pip
pip install -r monitoring/requirements-monitoring.txt
python3 monitoring/controller_exporter.py --controller-url "${LB_CONTROLLER_URL:-http://127.0.0.1:8080}" --listen-port "${EXPORTER_PORT:-9108}"
