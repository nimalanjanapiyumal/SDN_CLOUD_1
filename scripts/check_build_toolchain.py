#!/usr/bin/env python3
from __future__ import annotations

import sys
from importlib import metadata


def parse_nums(v: str) -> tuple[int, ...]:
    nums = []
    for part in v.split('.'):
        digits = ''.join(ch for ch in part if ch.isdigit())
        if not digits:
            break
        nums.append(int(digits))
    return tuple(nums or [0])


def get_ver(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return 'missing'


pip_v = get_ver('pip')
setuptools_v = get_ver('setuptools')
packaging_v = get_ver('packaging')
pbr_v = get_ver('pbr')
wheel_v = get_ver('wheel')

print(f'[INFO] pip={pip_v} setuptools={setuptools_v} packaging={packaging_v} wheel={wheel_v} pbr={pbr_v}')

errors: list[str] = []
if setuptools_v == 'missing' or parse_nums(setuptools_v) >= (71,):
    errors.append('setuptools must be installed and pinned below 71.0.0 for legacy Ryu builds')
if packaging_v == 'missing' or parse_nums(packaging_v) < (22,):
    errors.append('packaging must be installed at 22.0 or newer')
if wheel_v == 'missing':
    errors.append('wheel is missing')
if pbr_v == 'missing':
    errors.append('pbr is missing')

if errors:
    print('[ERROR] Build toolchain check failed:')
    for e in errors:
        print(f'  - {e}')
    sys.exit(1)

print('[OK] Build toolchain versions are compatible with patched Ryu install.')
