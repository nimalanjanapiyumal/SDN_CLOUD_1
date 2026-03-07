# Complete Steps to Run the Project

## 1. Recommended VM layout
- **VM-A1 Controller**: SDN controller + optional Flask dashboard
- **VM-A2 Dataplane**: Mininet + Open vSwitch + backend hosts
- Optional OpenStack services can be external to these VMs; the dashboard and scaler use `openstacksdk`.

## 2. Copy project to the VM
Use the **tar.gz** archive on Linux because it preserves shell execute permissions better than zip.

```bash
mkdir -p /home/user/SDN_CLOUD_1
cd /home/user
# copy or extract the folder here
```

## 3. Controller VM steps
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh fix-perms
bash manage.sh controller bootstrap
bash manage.sh controller start
bash manage.sh controller status
bash manage.sh controller logs
```

Expected controller ports:
- OpenFlow TCP: `6633`
- REST API: `8080`

Check:
```bash
ss -lntp | egrep '(:6633|:8080)'
curl http://127.0.0.1:8080/lb/status
```

## 4. Dashboard steps
If running on the same VM as the controller:
```bash
cd /home/user/SDN_CLOUD_1
bash start_parallel.sh
```

If running separately:
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dashboard bootstrap
export CONTROLLER_API_URL=http://<controller-ip>:8080
bash manage.sh dashboard start
bash manage.sh dashboard status
bash manage.sh dashboard logs
```

Open in browser:
- `http://<dashboard-ip>:5000`

## 5. Dataplane VM steps
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dataplane bootstrap
CTRL_IP=<controller-ip> bash manage.sh dataplane start
```

Once Mininet starts, test:
```bash
pingall
h1 curl http://10.0.0.100:8000
h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 20 --duration 15 --sla-ms 200
h1 python3 tools/iperf3_benchmark.py --server 10.0.0.100 --parallel 4 --time 15
```

## 6. Prometheus and Grafana
### Prometheus
Use the included config:
- `prometheus/prometheus.yml`

### Grafana
Import:
- `dashboard/grafana/hybrid_lb_dashboard.json`

## 7. OpenStack access
If you want the dashboard or scaler to interact with OpenStack:
1. Install and configure `clouds.yaml` or `OS_*` environment variables.
2. Test:
```bash
source /path/to/openrc.sh
python - <<'PY'
import openstack
conn = openstack.connect()
print([s.name for s in conn.compute.servers()][:5])
PY
```

## 8. Stop and restart
```bash
bash manage.sh controller stop
bash manage.sh dashboard stop
bash manage.sh stack restart
```

## 9. Logs
```bash
bash manage.sh controller logs
bash manage.sh dashboard logs
```

## 10. Most common issues
### Permission denied
```bash
bash manage.sh fix-perms
```

### Controller environment missing package
```bash
bash manage.sh controller bootstrap
```

### Dashboard cannot reach controller
Set the controller API URL before starting dashboard:
```bash
export CONTROLLER_API_URL=http://<controller-ip>:8080
bash manage.sh dashboard start
```
