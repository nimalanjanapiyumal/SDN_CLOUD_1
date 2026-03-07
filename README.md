# SDN Hybrid OpenStack Project (Direct Deploy Fixed)

> Important after extracting the archive:
> ```bash
> bash manage.sh fix-perms
> ```
>
> Then use the single launcher:
> ```bash
> bash manage.sh controller bootstrap
> bash manage.sh controller start
> ```


# SDN Hybrid Load Balancing Framework for OpenStack + Mininet

Ready-to-deploy project package for:
- OpenStack-backed cloud testbed
- Ryu SDN controller
- Hybrid RR + Genetic Algorithm load balancing
- Prometheus/Grafana monitoring
- Flask operator dashboard
- PyCharm + Git workflow

## What changed in this ready package
- Fixed the controller-side overload/stickiness logic by using explicit backend `max_connections` instead of normalizing by current maximum active connections.
- Split controller, dashboard, and dataplane dependencies so the dashboard venv does **not** try to install Ryu.
- Added an automated **patched Ryu installer** for Python 3.10+ that avoids the unsupported `--no-use-pep517` flag and falls back to `setup.py install` when needed.
- Added ready bootstrap scripts for controller, dataplane, and dashboard VMs.

## Folder layout
- `vm-a1-controller/` - Ryu app, hybrid algorithm, REST API, controller config
- `vm-a2-dataplane/` - Mininet topology and traffic tools
- `dashboard/flask_dashboard/` - operator dashboard for controller and OpenStack status
- `scripts/` - VM bootstrap and patched Ryu installer
- `prometheus/` - Prometheus scrape config
- `dashboard/grafana/` - example Grafana dashboard JSON
- `tests/` - smoke tests for hybrid logic
- `docs/` - deployment guides

## Fast deployment
### Controller VM
```bash
cd /home/user/CLOUD_1/SDN_CLOUD_1
bash scripts/bootstrap_controller_vm.sh
source .venv-controller/bin/activate
cd vm-a1-controller
./run_controller.sh
```

### Data-plane VM
```bash
cd /home/user/CLOUD_1/SDN_CLOUD_1
bash scripts/bootstrap_dataplane_vm.sh
cd vm-a2-dataplane
CTRL_IP=<controller-private-ip> ./run_mininet.sh
```

### Dashboard VM (or same controller VM)
```bash
cd /home/user/CLOUD_1/SDN_CLOUD_1
bash scripts/bootstrap_dashboard_vm.sh
source .venv-dashboard/bin/activate
export CONTROLLER_API_URL=http://<controller-private-ip>:8080
python dashboard/flask_dashboard/app.py
```

Open the dashboard at `http://<vm-ip>:5000`.


## Safer startup commands
```bash
bash manage.sh controller bootstrap
bash manage.sh controller start
bash manage.sh controller logs
```

To start controller + dashboard on the same VM:
```bash
bash start_parallel.sh
```
