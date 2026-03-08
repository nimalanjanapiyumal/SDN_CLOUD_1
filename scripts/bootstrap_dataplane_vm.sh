#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y
sudo apt-get install -y mininet openvswitch-switch iperf3 curl python3-pip
sudo systemctl enable openvswitch-switch || true
sudo systemctl start openvswitch-switch || true
echo '[OK] Dataplane packages ready.'
