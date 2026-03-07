#!/usr/bin/env python3
"""Mininet topology for Hybrid SDN Load Balancer demo."""

import argparse
from functools import partial
from pathlib import Path

from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.topo import Topo


class LbTopo(Topo):
    def build(self, servers: int = 3):
        s1 = self.addSwitch("s1")
        h1 = self.addHost("h1", ip="10.0.0.1/24", mac="00:00:00:00:00:01")
        self.addLink(h1, s1)
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

    project_root = Path(__file__).resolve().parents[1]
    backend_script = project_root / 'tools' / 'backend_server.py'

    for i in range(args.servers):
        h = net.get(f"h{i+2}")
        info(f"*** Starting JSON backend server on {h.name} ({h.IP()})\n")
        h.cmd("pkill -f 'backend_server.py' || true")
        h.cmd(f"nohup python3 {backend_script} --name {h.name} --ip {h.IP()} --port 8000 >/tmp/http_{h.name}.log 2>&1 &")
        h.cmd("pkill -f 'iperf3 -s -p 5201' || true")
        h.cmd("command -v iperf3 >/dev/null 2>&1 && nohup iperf3 -s -p 5201 >/tmp/iperf_%s.log 2>&1 &" % h.name)

    info("*** Mininet started. VIP is 10.0.0.100 (handled by controller)\n")
    info("*** Validation inside Mininet: h1 ping -c 2 10.0.0.100\n")
    info("*** HTTP test inside Mininet: h1 curl http://10.0.0.100:8000\n")
    info("*** HTTP benchmark: h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 20 --duration 20 --sla-ms 200 --json /tmp/http_20.json\n")
    info("*** iPerf benchmark: h1 python3 tools/iperf3_benchmark.py --vip 10.0.0.100 --port 5201 --duration 15 --parallel 4 --json /tmp/iperf.json\n")

    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    main()
