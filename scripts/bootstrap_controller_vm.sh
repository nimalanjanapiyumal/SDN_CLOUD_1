#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 -m venv .venv-controller
source .venv-controller/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r vm-a1-controller/requirements-controller.txt
python scripts/check_controller_env.py
echo '[OK] Controller environment ready.'
