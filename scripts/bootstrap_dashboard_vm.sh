#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 -m venv .venv-dashboard
source .venv-dashboard/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install 'Flask>=3.0' 'requests>=2.31' 'PyYAML>=6.0' 'openstacksdk>=1.5'
echo '[OK] Dashboard environment ready.'
