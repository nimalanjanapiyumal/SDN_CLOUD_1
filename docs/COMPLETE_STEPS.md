# Complete Steps to Run

## 1. Controller VM
```bash
cd /path/to/SDN_CLOUD_1/vm-a1-controller
python3 -m venv .venv-controller
source .venv-controller/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements-controller.txt
export SDN_HYBRID_LB_CONFIG=$(pwd)/config.controller.yaml
bash run_controller.sh
```

The controller exposes:
- OpenFlow on port `6633`
- REST API on port `8080`

## 2. Dataplane VM
```bash
cd /path/to/SDN_CLOUD_1/vm-a2-dataplane
CTRL_IP=<controller-ip> bash run_mininet.sh
```

Inside Mininet:
```bash
h1 ping -c 2 10.0.0.100
h1 curl http://10.0.0.100:8000
```

The response should be JSON showing the backend name.

## 3. Dashboard VM
```bash
cd /path/to/SDN_CLOUD_1
bash scripts/bootstrap_dashboard.sh
source .venv-dashboard/bin/activate
export CONTROLLER_API_URL=http://<controller-ip>:8080
bash dashboard/run_dashboard.sh
```

Open:
```text
http://<dashboard-vm-ip>:5050
```

## 4. OpenStack visibility
Choose one method.

### Method A: clouds.yaml
```bash
mkdir -p ~/.config/openstack
nano ~/.config/openstack/clouds.yaml
export OS_CLOUD=mycloud
```

### Method B: environment variables
```bash
export OS_AUTH_URL=http://<keystone-host>:5000/v3
export OS_USERNAME=<username>
export OS_PASSWORD=<password>
export OS_PROJECT_NAME=<project>
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
```

Then refresh the OpenStack page.

## 5. Testing and Evaluation
Inside Mininet:
```bash
h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 10 --duration 20 --sla-ms 200 --json /tmp/http_10.json
h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 20 --duration 20 --sla-ms 200 --json /tmp/http_20.json
h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 50 --duration 20 --sla-ms 200 --json /tmp/http_50.json
```

Optional iperf3:
```bash
h2 iperf3 -s -p 5201 &
h3 iperf3 -s -p 5201 &
h4 iperf3 -s -p 5201 &
h1 python3 tools/iperf3_benchmark.py --vip 10.0.0.100 --port 5201 --duration 15 --parallel 4 --json /tmp/iperf_4.json
```

Upload the JSON outputs on the **Testing & Evaluation** page to render graphs.
