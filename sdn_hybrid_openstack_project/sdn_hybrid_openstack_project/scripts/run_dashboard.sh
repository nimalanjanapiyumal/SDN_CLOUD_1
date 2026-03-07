#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv-dashboard
source .venv-dashboard/bin/activate
pip install --upgrade pip
pip install -r dashboard/requirements-dashboard.txt
python3 -m dashboard.app
