#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, socket, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def make_handler(name, ip):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = {'backend': name, 'backend_ip': ip, 'hostname': socket.gethostname(), 'path': self.path, 'timestamp': time.time()}
            payload = json.dumps(body).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        def log_message(self, fmt, *args):
            return
    return Handler

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--name', required=True); ap.add_argument('--ip', required=True); ap.add_argument('--port', type=int, default=8000); args = ap.parse_args()
    ThreadingHTTPServer(('0.0.0.0', args.port), make_handler(args.name, args.ip)).serve_forever()

if __name__ == '__main__':
    main()
