# Functional and Performance Test Plan

## Functional tests
### Controller availability
```bash
curl http://<controller-ip>:8080/lb/status
```
Expected: JSON response with VIP, backends, and weights.

### OpenFlow connectivity
On the controller VM:
```bash
sudo ss -lntp | egrep '(:6633|:8080|:5555|:9108)'
```
Expected: ports listening.

### Mininet traffic test
In Mininet:
```bash
pingall
h1 curl http://10.0.0.100:8000
```
Expected: successful response from one backend.

## Performance tests
### HTTP benchmark
```bash
h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 50 --duration 20 --sla-ms 200
```
Record:
- total requests
- req/s
- p50 latency
- p95 latency
- error rate
- SLA compliance

### iPerf throughput
```bash
h2 iperf3 -s -D
h3 iperf3 -s -D
h4 iperf3 -s -D
h1 iperf3 -c 10.0.0.100 -t 10
```

## Fault-tolerance test
1. Mark one backend unhealthy from dashboard or REST API.
2. Repeat HTTP benchmark.
3. Verify traffic is rerouted to remaining healthy servers.

## Scalability discussion
The practical demo uses three Mininet backends, but the architecture scales by:
- adding more backend hosts to the topology
- increasing GA population/generations carefully
- running Prometheus/Grafana externally if needed
- using OpenStack to resize VM flavors or create more experiment VMs
