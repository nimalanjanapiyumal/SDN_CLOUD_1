#!/usr/bin/env bash
set -euo pipefail

sudo apt update
sudo apt install -y git curl python3 python3-pip mininet openvswitch-switch iperf3 netcat-openbsd
sudo systemctl enable openvswitch-switch
sudo systemctl restart openvswitch-switch
