# Complete Steps

## Controller VM

```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh fix-perms
bash manage.sh controller bootstrap
bash manage.sh controller start
bash manage.sh controller status
bash manage.sh controller logs
bash manage.sh controller diag
```

Check controller ports:

```bash
ss -lntp | grep 6633
ss -lntp | grep 8080
```

Find controller IP:

```bash
ip route get 1.1.1.1 | awk '{print $7; exit}'
```

## Dataplane VM

```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dataplane bootstrap
CTRL_IP=<controller-ip> bash manage.sh dataplane start
```

Inside Mininet:

```bash
h1 ping -c 2 10.0.0.100
h1 curl http://10.0.0.100:8000
ovs-vsctl show
ovs-ofctl -O OpenFlow13 dump-flows s1
```

## Dashboard

```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh dashboard bootstrap
export CONTROLLER_API_URL=http://<controller-ip>:8080
bash manage.sh dashboard start
```
