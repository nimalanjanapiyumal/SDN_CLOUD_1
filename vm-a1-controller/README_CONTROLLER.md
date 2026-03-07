# VM-A1 Controller Setup

This VM runs the SDN controller for the hybrid load balancer.

## Start with the project root helpers
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh fix-perms
bash manage.sh controller bootstrap
bash manage.sh controller start
bash manage.sh controller status
bash manage.sh controller logs
```

## Manual start from the controller folder
```bash
cd /home/user/SDN_CLOUD_1
source .venv-controller/bin/activate
cd vm-a1-controller
bash ./run_controller.sh
```

## REST check
```bash
curl http://127.0.0.1:8080/lb/status
```
