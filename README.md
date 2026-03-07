# SDN-Based Adaptive Cloud Network Management Framework (Fresh Deployable Package)

This package is a fresh deployable version of your project for:
- OpenStack-based cloud testbed
- SDN control plane with a hybrid Round Robin + Genetic Algorithm load balancer
- Prometheus/Grafana monitoring
- Flask operator dashboard
- Mininet dataplane emulation

## Important implementation note
The original project used Ryu. This package runs the controller on **OS-Ken**, which is the OpenStack-maintained fork of Ryu and keeps the same overall controller model for this project. This avoids the repeated Ryu packaging failures on Python 3.10.

## Folder layout
- `vm-a1-controller/` controller code, config, runner
- `vm-a2-dataplane/` Mininet topology and test tools
- `dashboard/` Flask dashboard and Grafana JSON
- `scripts/` bootstrap and helper scripts
- `prometheus/` Prometheus scrape config
- `docs/` complete run steps
- `manage.sh` one-command launcher per role
- `start_parallel.sh` bootstrap+start controller and dashboard on the same VM

## Fastest path
### Controller VM
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh fix-perms
bash manage.sh controller bootstrap
bash manage.sh controller start
bash manage.sh controller status
bash manage.sh controller logs
```

### Dashboard VM (or same VM)
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dashboard bootstrap
export CONTROLLER_API_URL=http://<controller-ip>:8080
bash manage.sh dashboard start
bash manage.sh dashboard logs
```

### Dataplane VM
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dataplane bootstrap
CTRL_IP=<controller-ip> bash manage.sh dataplane start
```

Then inside Mininet:
```bash
h1 curl http://10.0.0.100:8000
h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 20 --duration 15 --sla-ms 200
```

See `docs/COMPLETE_STEPS.md` for the full runbook.
