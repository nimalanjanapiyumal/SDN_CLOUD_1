# SDN-Based Adaptive Cloud Network Management Framework

This package combines the original controller and dataplane code with a redesigned Flask dashboard for:
- live SDN overview
- professional backend/resource visualization
- separate OpenStack visibility page
- separate testing and evaluation page
- benchmark JSON upload and graphing

## Quick start

### 1) Controller VM
```bash
cd vm-a1-controller
python3 -m venv .venv-controller
source .venv-controller/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements-controller.txt
export SDN_HYBRID_LB_CONFIG=$(pwd)/config.controller.yaml
bash run_controller.sh
```

### 2) Dataplane VM
```bash
cd vm-a2-dataplane
bash run_mininet.sh
```
If controller is remote:
```bash
CTRL_IP=<controller-ip> bash run_mininet.sh
```

### 3) Dashboard VM or same VM
```bash
cd <project-root>
bash scripts/bootstrap_dashboard.sh
source .venv-dashboard/bin/activate
export CONTROLLER_API_URL=http://<controller-ip>:8080
bash dashboard/run_dashboard.sh
```
Open: `http://<dashboard-vm-ip>:5050`

## Dashboard pages
- **Overview**: backend health, flow counts, throughput, utilization, GA weights
- **OpenStack**: configuration checklist, server visibility, networks
- **Testing & Evaluation**: plan, metrics, benchmark uploads, graphs, testing buttons

## Notes
- `10.0.0.100:8000` is the VIP inside Mininet; test it from `h1` inside Mininet.
- Prometheus is optional. OpenFlow port statistics still provide flow count and bandwidth-derived metrics.
