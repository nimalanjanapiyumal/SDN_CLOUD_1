# SDN Hybrid OpenStack Project - Visual and Evaluation Update

This version improves three areas:

1. A clearer Flask dashboard with backend health cards, utilization bars, OpenStack status, and a testing matrix.
2. Better OpenStack handling so missing Keystone credentials show as `not configured` instead of a vague crash.
3. Stronger testing support for section 3.1.5, including JSON backend responses, HTTP benchmark JSON output, iperf3 JSON output, and a dedicated testing guide.

## Key reminder

The VIP `10.0.0.100:8000` lives inside the **Mininet network**. Test it from **h1 inside the Mininet CLI**, not from the controller VM shell.

## Quick start

### Controller VM

```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh fix-perms
bash manage.sh controller bootstrap
bash manage.sh controller start
bash manage.sh controller logs
```

### Dashboard VM or same VM

```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dashboard bootstrap
export CONTROLLER_API_URL=http://<controller-ip>:8080
# optional for OpenStack visibility:
# export OS_CLOUD=mycloud
# or export OS_AUTH_URL / OS_USERNAME / OS_PASSWORD / OS_PROJECT_NAME / OS_USER_DOMAIN_NAME / OS_PROJECT_DOMAIN_NAME
bash manage.sh dashboard start
bash manage.sh dashboard logs
```

### Dataplane VM

```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dataplane bootstrap
CTRL_IP=<controller-ip> bash manage.sh dataplane start
```

Inside Mininet:

```bash
h1 ping -c 2 10.0.0.100
h1 curl http://10.0.0.100:8000
h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 20 --duration 20 --sla-ms 200 --json /tmp/http_20.json
h1 python3 tools/iperf3_benchmark.py --vip 10.0.0.100 --port 5201 --duration 15 --parallel 4 --json /tmp/iperf.json
```

## Important docs

- `docs/COMPLETE_STEPS.md`
- `docs/TESTING_EVALUATION.md`
- `docs/OPENSTACK_QUICK_CONFIG.md`
