#!/usr/bin/env python3
import argparse, time, socket
from functools import partial
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.topo import Topo
from mininet.util import quietRun

class LbTopo(Topo):
    def build(self, servers=3):
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        self.addLink(h1, s1)
        ips = ['10.0.0.2/24','10.0.0.3/24','10.0.0.4/24','10.0.0.5/24']
        macs = ['00:00:00:00:00:02','00:00:00:00:00:03','00:00:00:00:00:04','00:00:00:00:00:05']
        for i in range(servers):
            h = self.addHost(f'h{i+2}', ip=ips[i], mac=macs[i])
            self.addLink(h, s1)

def tcp_probe(ip, port, timeout=2.0):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--controller-ip', default='127.0.0.1'); ap.add_argument('--controller-port', type=int, default=6633); ap.add_argument('--servers', type=int, default=3, choices=[1,2,3,4]); args = ap.parse_args()
    info(f'*** Checking controller reachability: {args.controller_ip}:{args.controller_port}\n')
    info('*** Controller TCP port reachable before Mininet start\n' if tcp_probe(args.controller_ip, args.controller_port) else '*** WARNING: Controller TCP port not reachable yet. OpenFlow handshake may fail until it is listening.\n')
    net = Mininet(topo=LbTopo(servers=args.servers), controller=lambda name: RemoteController(name, ip=args.controller_ip, port=args.controller_port), switch=partial(OVSSwitch, protocols='OpenFlow13'), autoSetMacs=False, autoStaticArp=False)
    net.start(); time.sleep(2)
    info('*** OVS controller setting for s1:\n' + quietRun('ovs-vsctl get-controller s1') + '\n')
    info('*** OVS show:\n' + quietRun('ovs-vsctl show') + '\n')
    info('*** OpenFlow switch info:\n' + quietRun('ovs-ofctl -O OpenFlow13 show s1') + '\n')
    for i in range(args.servers):
        h = net.get(f'h{i+2}'); name=f'srv{i+1}'
        info(f'*** Starting backend JSON server on {h.name} ({h.IP()})\n')
        h.cmd("pkill -f 'backend_server.py' || true")
        h.cmd(f"nohup python3 tools/backend_server.py --name {name} --ip {h.IP()} --port 8000 >/tmp/{name}_http.log 2>&1 &")
        h.cmd("pkill -f 'iperf3 -s -p 5201' || true")
        h.cmd("nohup iperf3 -s -p 5201 >/tmp/iperf_%s.log 2>&1 &" % name)
    info('*** Mininet started. VIP is 10.0.0.100 (handled by controller)\n')
    info('*** Verify OpenFlow from Mininet CLI: sh ovs-vsctl show ; sh ovs-ofctl -O OpenFlow13 dump-flows s1\n')
    info('*** Test VIP: h1 ping -c 2 10.0.0.100 ; h1 curl http://10.0.0.100:8000 ; h1 ip neigh show\n')
    CLI(net); net.stop()

if __name__ == '__main__':
    setLogLevel('info'); main()
