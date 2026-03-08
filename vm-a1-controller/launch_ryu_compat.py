#!/usr/bin/env python3
from __future__ import annotations
import os, sys, warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

def patch_eventlet():
    try:
        import eventlet.wsgi as ew
        if not hasattr(ew, 'ALREADY_HANDLED'):
            ew.ALREADY_HANDLED = object()
    except Exception:
        pass

def main():
    patch_eventlet()
    ofp = os.environ.get('OFP_PORT', '6633')
    rest = os.environ.get('REST_PORT', '8080')
    app = os.environ.get('RYU_APP', 'sdn_hybrid_lb/controller/ryu_app.py')
    sys.argv = ['ryu-manager', '--ofp-tcp-listen-port', str(ofp), '--wsapi-port', str(rest), app]
    from ryu.cmd.manager import main as ryu_main
    ryu_main()

if __name__ == '__main__':
    main()
