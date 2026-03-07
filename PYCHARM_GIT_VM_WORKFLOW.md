# PyCharm + Git + VM Workflow

## 1. Open the project in PyCharm
1. Start PyCharm.
2. Choose **Open** and select the project root.
3. Create one interpreter for the controller/dashboard work:
   - **Settings → Python Interpreter → Add Interpreter → Virtualenv**
   - Use Python 3.10+ if available.
4. Install dependencies from the required files:
   ```bash
   pip install -r vm-a1-controller/requirements-controller.txt
   pip install -r dashboard/requirements-dashboard.txt
   pip install -r monitoring/requirements-monitoring.txt
   ```

## 2. Suggested Run Configurations
### Controller
- Working directory: `vm-a1-controller`
- Script: `run_controller.sh`
- Environment:
  - `CONFIG=./config.controller.yaml`
  - `OFP_PORT=6633`
  - `REST_PORT=8080`

### Dashboard
- Module name: `dashboard.app`
- Working directory: project root
- Environment:
  - `LB_CONTROLLER_URL=http://127.0.0.1:8080`
  - `DASHBOARD_PORT=5555`

### Exporter
- Script: `monitoring/controller_exporter.py`
- Parameters:
  - `--controller-url http://127.0.0.1:8080 --listen-port 9108`

## 3. Put the project into Git
### Option A – your own remote repository
```bash
git init
git add .
git commit -m "Initial SDN hybrid OpenStack project"
git remote add origin https://github.com/<your-user>/sdn-hybrid-openstack-project.git
git push -u origin main
```
Then on each VM:
```bash
git clone https://github.com/<your-user>/sdn-hybrid-openstack-project.git
```

### Option B – clone from the bundle file
This package also includes a Git bundle artifact. Copy the bundle to a VM and run:
```bash
git clone sdn_hybrid_openstack_project.bundle sdn-hybrid-openstack-project
```

## 4. Controller VM workflow
```bash
ssh ubuntu@<controller-vm-ip>
cd ~
git clone <repo-or-bundle>
cd sdn-hybrid-openstack-project
bash scripts/bootstrap_controller_vm.sh
cd vm-a1-controller
./run_controller.sh
```

## 5. Data plane VM workflow
```bash
ssh ubuntu@<dataplane-vm-ip>
cd ~
git clone <repo-or-bundle>
cd sdn-hybrid-openstack-project
bash scripts/bootstrap_dataplane_vm.sh
cd vm-a2-dataplane
CTRL_IP=<controller-private-ip> ./run_mininet.sh
```

## 6. Good PyCharm project habits
- Keep the repo root open in PyCharm.
- Use separate terminal tabs for controller, dashboard, and tests.
- Store secrets in environment variables or `clouds.yaml`, not in Git.
- Commit config templates, not real credentials.
