# 2-VM Deployment Summary

- **VM-A1** = Controller VM (`vm-a1-controller/`)
- **VM-A2** = Data Plane VM (`vm-a2-dataplane/`)

Recommended order:
1. Deploy VMs in OpenStack Horizon.
2. Clone the repo or clone the Git bundle on both VMs.
3. Bootstrap Controller VM.
4. Bootstrap Data Plane VM.
5. Start the controller.
6. Start Mininet.
7. Run benchmark and collect metrics.
8. Open the Flask dashboard and Grafana dashboard if enabled.
