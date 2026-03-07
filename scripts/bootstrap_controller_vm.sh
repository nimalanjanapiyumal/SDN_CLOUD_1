#!/usr/bin/env bash
set -euo pipefail

sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl netcat-openbsd

python3 -m venv .venv-controller
source .venv-controller/bin/activate
pip install --upgrade pip
pip install -r vm-a1-controller/requirements-controller.txt
