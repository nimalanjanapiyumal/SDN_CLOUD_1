# Deployment Steps

## 1. Repair permissions after unzip
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh fix-perms
```

## 2. Controller VM
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh controller bootstrap
bash manage.sh controller start
bash manage.sh controller status
```
Logs:
```bash
tail -f logs/controller.log
```

## 3. Dashboard VM
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dashboard bootstrap
bash manage.sh dashboard start
bash manage.sh dashboard status
```
Logs:
```bash
tail -f logs/dashboard.log
```

## 4. Dataplane VM
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dataplane bootstrap
CTRL_IP=<controller_private_ip> bash manage.sh dataplane start
```

## 5. If you still want to run scripts directly
```bash
cd vm-a1-controller
bash ./run_controller.sh
```

Using `bash ./run_controller.sh` works even if the execute bit was lost during extraction.
