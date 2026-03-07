#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import socket
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    server_version = 'HybridBackend/1.0'

    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        payload = {
            'backend_name': self.server.backend_name,
            'backend_ip': self.server.backend_ip,
            'hostname': socket.gethostname(),
            'path': self.path,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'message': 'Hybrid LB backend response',
        }
        body = json.dumps(payload, indent=2).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', required=True)
    ap.add_argument('--ip', required=True)
    ap.add_argument('--port', type=int, default=8000)
    args = ap.parse_args()

    httpd = ThreadingHTTPServer(('0.0.0.0', args.port), Handler)
    httpd.backend_name = args.name
    httpd.backend_ip = args.ip
    httpd.serve_forever()


if __name__ == '__main__':
    main()
