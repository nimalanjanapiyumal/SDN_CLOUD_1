# 3.1.5 Testing and Evaluation

This project supports the three required evaluation areas.

## 1) Functional testing

Use these checks after the controller and Mininet are running:

```bash
# from controller VM
bash manage.sh controller status
curl http://127.0.0.1:8080/lb/status

# inside Mininet CLI
h1 ping -c 2 10.0.0.100
h1 curl http://10.0.0.100:8000
```

Expected result:
- `h1` learns the VIP MAC via ARP.
- `curl` returns JSON from one of the backends (`h2`, `h3`, or `h4`).
- The controller dashboard shows active flows increasing.

Health and failover test:

```bash
curl -X POST http://127.0.0.1:8080/lb/health/srv1 -H 'Content-Type: application/json' -d '{"healthy": false}'
```

Then repeat `h1 curl http://10.0.0.100:8000` and confirm traffic is handled by another backend.

## 2) Performance and scalability testing

HTTP benchmark for latency, throughput, and SLA compliance:

```bash
# inside Mininet CLI
h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 10 --duration 20 --sla-ms 200 --json /tmp/http_10.json
h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 20 --duration 20 --sla-ms 200 --json /tmp/http_20.json
h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 50 --duration 20 --sla-ms 200 --json /tmp/http_50.json
```

Record these metrics from each JSON file:
- throughput_req_per_s
- latency_p50_ms
- latency_p95_ms
- error_rate_pct
- sla_compliance_pct

For network throughput with multiple streams:

```bash
# inside Mininet CLI
h1 python3 tools/iperf3_benchmark.py --vip 10.0.0.100 --port 5201 --duration 15 --parallel 4 --json /tmp/iperf_4.json
h1 python3 tools/iperf3_benchmark.py --vip 10.0.0.100 --port 5201 --duration 15 --parallel 8 --json /tmp/iperf_8.json
```

Track:
- throughput_mbps
- retransmits
- the effect of parallel streams on aggregate bandwidth

## 3) Fault tolerance and SLA compliance

Simulate faults using either the dashboard toggle or the REST API:

```bash
curl -X POST http://127.0.0.1:8080/lb/health/srv2 -H 'Content-Type: application/json' -d '{"healthy": false}'
```

Then rerun the HTTP benchmark and compare:
- request throughput before and after failure
- p95 latency before and after failure
- SLA compliance percentage before and after failure
- error-rate spike duration

## Resource and monitoring metrics

The controller already tracks:
- active flows
- backend throughput in Mbps using OpenFlow port statistics
- bandwidth utilization percentage per backend
- backend health status

Optional Prometheus integration adds:
- CPU utilization per backend
- memory utilization per backend

Enable it in `vm-a1-controller/config.controller.yaml` and map each backend instance to its exporter target.

## OpenStack integration note

If the dashboard shows `Auth plugin requires parameters which were not given: auth_url`, configure OpenStack with either:
- `OS_CLOUD` and a valid `clouds.yaml`, or
- Keystone environment variables such as `OS_AUTH_URL`, `OS_USERNAME`, `OS_PASSWORD`, and `OS_PROJECT_NAME`.

The VIP `10.0.0.100:8000` exists inside the Mininet network. Test it from `h1`, not from the controller VM shell.
