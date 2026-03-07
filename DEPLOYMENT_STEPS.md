
# Direct deployment steps

## 1. Copy project to VMs
```bash
scp -r sdn_hybrid_openstack_project_ready user@controller-vm:/home/user/CLOUD_1/SDN_CLOUD_1
scp -r sdn_hybrid_openstack_project_ready user@dataplane-vm:/home/user/CLOUD_1/SDN_CLOUD_1
```

## 2. Controller VM
```bash
cd /home/user/CLOUD_1/SDN_CLOUD_1
bash scripts/bootstrap_controller_vm.sh
source .venv-controller/bin/activate
python -m pytest -q tests
cd vm-a1-controller
./run_controller.sh
```

## 3. Dataplane VM
```bash
cd /home/user/CLOUD_1/SDN_CLOUD_1
bash scripts/bootstrap_dataplane_vm.sh
cd vm-a2-dataplane
CTRL_IP=<controller-private-ip> ./run_mininet.sh
```

## 4. Dashboard
```bash
cd /home/user/CLOUD_1/SDN_CLOUD_1
bash scripts/bootstrap_dashboard_vm.sh
source .venv-dashboard/bin/activate
export CONTROLLER_API_URL=http://<controller-private-ip>:8080
python dashboard/flask_dashboard/app.py
```
