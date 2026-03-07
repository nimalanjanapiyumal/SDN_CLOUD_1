# Deployment Steps

## 1) Extract
Prefer the `.tar.gz` archive on Linux because it preserves script permissions better.

```bash
cd /home/user
mkdir -p SDN_CLOUD_1
cd SDN_CLOUD_1
# extract the provided archive here
bash manage.sh fix-perms
```

## 2) Controller VM
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh controller bootstrap
bash manage.sh controller start
bash manage.sh controller status
bash manage.sh controller logs
```

## 3) Dashboard VM or same controller VM
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dashboard bootstrap
bash manage.sh dashboard start
bash manage.sh dashboard status
bash manage.sh dashboard logs
```

## 4) Start both controller and dashboard on one VM
```bash
cd /home/user/SDN_CLOUD_1
bash start_parallel.sh
```

## 5) Dataplane VM
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dataplane bootstrap
CTRL_IP=<controller_private_ip> bash manage.sh dataplane start
```
