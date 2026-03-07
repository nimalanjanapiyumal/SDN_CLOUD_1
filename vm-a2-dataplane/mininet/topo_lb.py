#!/usr/bin/env python3
"""Mininet topology for Hybrid SDN Load Balancer demo.

Topology:
    h1 ---\
    h2 ---- s1 ---- (remote Ryu controller)
    h3 ---/
    h4 --/

VIP (not assigned to a host): 10.0.0.100

Backends run: python3 -m http.server 8000
"""

import argparse
import time

from functools import partial

from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.topo import Topo


class LbTopo(Topo):
    def build(self, servers: int = 3):
        s1 = self.addSwitch("s1")

        # client
        h1 = self.addHost("h1", ip="10.0.0.1/24", mac="00:00:00:00:00:01")
        self.addLink(h1, s1)

        # servers
        server_ips = ["10.0.0.2/24", "10.0.0.3/24", "10.0.0.4/24", "10.0.0.5/24"]
        server_macs = ["00:00:00:00:00:02", "00:00:00:00:00:03", "00:00:00:00:00:04", "00:00:00:00:00:05"]
        for i in range(servers):
            name = f"h{i+2}"
            host = self.addHost(name, ip=server_ips[i], mac=server_macs[i])
            self.addLink(host, s1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--controller-ip", default="127.0.0.1")
    parser.add_argument("--controller-port", type=int, default=6633)
    parser.add_argument("--servers", type=int, default=3, choices=[1, 2, 3, 4])
    args = parser.parse_args()

    topo = LbTopo(servers=args.servers)

    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController(name, ip=args.controller_ip, port=args.controller_port),
        switch=partial(OVSSwitch, protocols='OpenFlow13'),
        autoSetMacs=False,
        autoStaticArp=False,
    )

    net.start()

    # Start simple HTTP servers on backends
    for i in range(args.servers):
        h = net.get(f"h{i+2}")
        info(f"*** Starting HTTP server on {h.name} ({h.IP()})\n")
        h.cmd("pkill -f 'http.server 8000' || true")
        h.cmd("nohup python3 -m http.server 8000 >/tmp/http_%s.log 2>&1 &" % h.name)

    info("*** Mininet started. VIP is 10.0.0.100 (handled by controller)\n")
    info("*** Try: h1 curl http://10.0.0.100:8000\n")

    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    main()
