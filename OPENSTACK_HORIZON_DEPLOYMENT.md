# OpenStack Horizon Deployment Guide

This project uses **OpenStack to host the two experiment VMs**:
- **Controller VM** – Ryu SDN controller, dashboard, exporter.
- **Data Plane VM** – Mininet, OVS, iPerf, benchmark tools.

## Recommended flavor sizing
### Controller VM
- 2 vCPU
- 4 GB RAM
- 20+ GB disk

### Data Plane VM
- 4 vCPU
- 8 GB RAM
- 30+ GB disk

## Recommended OpenStack network plan
Create a private network for controller ↔ data plane communication.

Example:
- Network: `sdn-hybrid-net`
- Subnet: `10.10.10.0/24`
- Controller VM private IP: `10.10.10.10`
- Data plane VM private IP: `10.10.10.11`

## Horizon steps
### 1. Create or import a key pair
**Project → Compute → Key Pairs → Import Public Key**

### 2. Create a security group
**Project → Network → Security Groups**

Add inbound rules for:
- TCP 22 (SSH)
- TCP 6633 (OpenFlow)
- TCP 8080 (controller REST API)
- TCP 5555 (Flask dashboard)
- TCP 9108 (controller exporter)
- TCP 9090 (Prometheus, optional)
- TCP 3000 (Grafana, optional)
- ICMP (optional, easier troubleshooting)

### 3. Create private network and subnet
**Project → Network → Networks → Create Network**

Suggested values:
- Network name: `sdn-hybrid-net`
- Subnet name: `sdn-hybrid-subnet`
- CIDR: `10.10.10.0/24`

### 4. Attach a router if floating IP access is needed
**Project → Network → Routers**
- Create router
- Set external network / gateway
- Add interface to `sdn-hybrid-subnet`

### 5. Launch Controller VM
**Project → Compute → Instances → Launch Instance**
- Name: `sdn-hybrid-controller`
- Image: Ubuntu 22.04 (recommended)
- Flavor: controller flavor
- Networks: `sdn-hybrid-net`
- Security Group: the SG created above
- Key Pair: your SSH key

### 6. Launch Data Plane VM
- Name: `sdn-hybrid-dataplane`
- Image: Ubuntu 22.04
- Flavor: larger flavor than controller
- Networks: `sdn-hybrid-net`
- Security Group: same SG
- Key Pair: same SSH key

### 7. Allocate floating IPs if external SSH is required
Attach floating IPs to each VM.

### 8. Verify internal connectivity
From the data plane VM:
```bash
ping -c 3 10.10.10.10
nc -vz 10.10.10.10 6633
```

## Horizon as the operational dashboard
Use Horizon for:
- power on/off and reboot
- floating IP association
- security group rules
- instance console access
- network/router inspection
- quota and flavor visibility

The included **Flask dashboard** complements Horizon by providing **load-balancer-specific controls**.

## Optional SDK-based provisioning
If you prefer code over manual Horizon steps, use:
```bash
python3 infra/openstack/provision_lab.py --help
```
This script assumes the image, network, key pair, and security groups already exist.
