# Complete steps to run the project

## 1. Controller VM

```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh fix-perms
bash manage.sh controller bootstrap
bash manage.sh controller start
bash manage.sh controller logs
```

Find the controller IP:

```bash
ip route get 1.1.1.1 | awk '{print $7; exit}'
```

## 2. Dashboard VM or same VM

```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dashboard bootstrap
export CONTROLLER_API_URL=http://<controller-ip>:8080
```

If you want OpenStack visibility, use either `OS_CLOUD` or the Keystone environment variables described in `docs/OPENSTACK_QUICK_CONFIG.md`.

Then start:

```bash
bash manage.sh dashboard start
bash manage.sh dashboard logs
```

Open the dashboard in the browser on port 5000.

## 3. Dataplane VM

```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dataplane bootstrap
CTRL_IP=<controller-ip> bash manage.sh dataplane start
```

## 4. Mininet validation

Inside the Mininet CLI, run:

```bash
h1 ping -c 2 10.0.0.100
h1 curl http://10.0.0.100:8000
```

The reply should be JSON from one of the backend hosts.

## 5. Testing and metrics

HTTP benchmark:

```bash
h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 20 --duration 20 --sla-ms 200 --json /tmp/http_20.json
```

iperf3 benchmark:

```bash
h1 python3 tools/iperf3_benchmark.py --vip 10.0.0.100 --port 5201 --duration 15 --parallel 4 --json /tmp/iperf.json
```

Fault-tolerance test:

```bash
curl -X POST http://127.0.0.1:8080/lb/health/srv1 -H 'Content-Type: application/json' -d '{"healthy": false}'
```

Then rerun the HTTP benchmark and compare throughput, p95 latency, and SLA compliance.
