# VM-A2 (Data Plane VM) Setup

This VM runs:
- Mininet topology
- OVS switch connected to the remote Ryu controller
- benchmark tools for HTTP and iPerf

## Quick start
From the project root on the data-plane VM:
```bash
bash scripts/bootstrap_dataplane_vm.sh
cd vm-a2-dataplane
CTRL_IP=<controller-private-ip> ./run_mininet.sh
```

## Inside Mininet
```bash
pingall
h1 curl http://10.0.0.100:8000
h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 50 --duration 20 --sla-ms 200
```

## Cleanup
```bash
sudo mn -c
sudo systemctl restart openvswitch-switch
```
