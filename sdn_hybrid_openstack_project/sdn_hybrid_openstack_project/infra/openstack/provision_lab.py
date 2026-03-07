#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ is None or __package__ == '':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from infra.openstack.openstack_manager import OpenStackManager, OpenStackSettings


def main() -> None:
    ap = argparse.ArgumentParser(description='Provision controller and data-plane VMs in OpenStack.')
    ap.add_argument('--cloud', default=None, help='OpenStack cloud profile name from clouds.yaml')
    ap.add_argument('--image', default=None, help='Image name or ID')
    ap.add_argument('--flavor', default=None, help='Flavor name or ID')
    ap.add_argument('--network', default=None, help='Network name or ID')
    ap.add_argument('--key-name', default=None, help='Key pair name')
    ap.add_argument('--security-groups', default=None, help='Comma-separated security groups')
    ap.add_argument('--controller-name', default='sdn-hybrid-controller')
    ap.add_argument('--dataplane-name', default='sdn-hybrid-dataplane')
    ap.add_argument('--floating-ip', action='store_true', help='Attach floating IPs if OS_EXTERNAL_NETWORK is set')
    args = ap.parse_args()

    settings = OpenStackSettings.from_env()
    if args.cloud:
        settings.cloud = args.cloud
    if args.image:
        settings.image = args.image
    if args.flavor:
        settings.flavor = args.flavor
    if args.network:
        settings.network = args.network
    if args.key_name:
        settings.key_name = args.key_name
    if args.security_groups:
        settings.security_groups = [s.strip() for s in args.security_groups.split(',') if s.strip()]

    manager = OpenStackManager(settings)
    summary = {
        'controller': manager.create_server(name=args.controller_name, auto_floating_ip=args.floating_ip),
        'dataplane': manager.create_server(name=args.dataplane_name, auto_floating_ip=args.floating_ip),
    }
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
