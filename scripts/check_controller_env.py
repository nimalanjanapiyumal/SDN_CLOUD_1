#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys

REQUIRED = [
    ("yaml", "PyYAML"),
    ("webob", "WebOb"),
    ("routes", "routes"),
    ("eventlet", "eventlet"),
    ("netaddr", "netaddr"),
    ("oslo_config", "oslo.config"),
    ("ovs", "ovs"),
    ("tinyrpc", "tinyrpc"),
    ("msgpack", "msgpack"),
    ("requests", "requests"),
    ("prometheus_client", "prometheus_client"),
    ("ryu", "ryu"),
]

missing: list[str] = []
for module_name, package_name in REQUIRED:
    try:
        importlib.import_module(module_name)
    except Exception as exc:
        missing.append(f"{package_name} ({module_name}): {exc}")

if missing:
    print("[ERROR] Controller environment is missing required modules:")
    for item in missing:
        print(f"  - {item}")
    print("[HINT] Re-run: bash manage.sh controller bootstrap")
    sys.exit(1)

print("[OK] Controller Python dependencies verified.")
