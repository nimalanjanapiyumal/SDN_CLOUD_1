#!/usr/bin/env python3
mods=['yaml','ryu','webob','eventlet','netaddr','requests']
missing=[]
for m in mods:
    try:
        __import__(m)
    except Exception:
        missing.append(m)
if missing:
    raise SystemExit('Missing controller modules: ' + ', '.join(missing))
print('[OK] Controller Python dependencies verified.')
