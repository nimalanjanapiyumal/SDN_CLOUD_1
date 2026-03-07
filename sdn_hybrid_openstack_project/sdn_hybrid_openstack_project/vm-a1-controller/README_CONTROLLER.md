# VM-A1 (Controller VM) Setup

This VM runs:
- Ryu SDN controller
- Hybrid RR + GA load-balancing logic
- REST API
- optional Flask dashboard and Prometheus exporter

## Quick start
From the project root on the controller VM:
```bash
bash scripts/bootstrap_controller_vm.sh
cd vm-a1-controller
./run_controller.sh
```

## REST API checks
```bash
curl http://localhost:8080/lb/status
curl -X POST http://localhost:8080/lb/recompute
curl -X POST http://localhost:8080/lb/health/srv2 -H 'Content-Type: application/json' -d '{"healthy": false}'
```

## Optional dashboard
```bash
source ../.venv-controller/bin/activate || true
pip install -r ../dashboard/requirements-dashboard.txt
LB_CONTROLLER_URL=http://127.0.0.1:8080 python3 -m dashboard.app
```

## Optional exporter
```bash
source ../.venv-controller/bin/activate || true
pip install -r ../monitoring/requirements-monitoring.txt
python3 ../monitoring/controller_exporter.py --controller-url http://127.0.0.1:8080 --listen-port 9108
```
