# Deployment Steps

## 1. Repair permissions after extract
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
bash manage.sh controller logs
```

## 3. Dashboard VM
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dashboard bootstrap
bash manage.sh dashboard start
bash manage.sh dashboard status
bash manage.sh dashboard logs
```

## 4. Controller + dashboard on the same VM
```bash
cd /home/user/SDN_CLOUD_1
bash start_parallel.sh
```

## 5. Dataplane VM
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dataplane bootstrap
CTRL_IP=<controller_private_ip> bash manage.sh dataplane start
```
