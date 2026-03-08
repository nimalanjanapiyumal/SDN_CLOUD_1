#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--vip', required=True); ap.add_argument('--port', type=int, default=5201); ap.add_argument('--duration', type=int, default=10); ap.add_argument('--parallel', type=int, default=1); ap.add_argument('--json', dest='json_path'); args = ap.parse_args()
    cp = subprocess.run(['iperf3','-c',args.vip,'-p',str(args.port),'-t',str(args.duration),'-P',str(args.parallel),'-J'], capture_output=True, text=True)
    if cp.returncode != 0: raise SystemExit(cp.stderr or cp.stdout)
    raw = json.loads(cp.stdout); end = raw.get('end', {}); total = (end.get('sum_received') or end.get('sum') or {})
    out = {'vip': args.vip, 'port': args.port, 'duration': args.duration, 'parallel': args.parallel, 'mbps': round(float(total.get('bits_per_second',0.0))/1_000_000.0,2), 'retransmits': total.get('retransmits'), 'raw': raw}
    print(json.dumps(out, indent=2))
    if args.json_path:
        with open(args.json_path, 'w', encoding='utf-8') as f: json.dump(out, f, indent=2)

if __name__ == '__main__':
    main()
