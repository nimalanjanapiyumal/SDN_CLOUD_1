#!/usr/bin/env python3
"""iperf3 benchmark helper."""

import argparse
import json
import subprocess
import sys


def run_iperf3(vip: str, port: int, duration: int, parallel: int):
    cmd = ["iperf3", "-c", vip, "-p", str(port), "-t", str(duration), "-P", str(parallel), "-J"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    data = json.loads(p.stdout)
    end = data.get('end', {})
    recv = end.get('sum_received', {}) or end.get('sum', {})
    sent = end.get('sum_sent', {}) or {}
    return {
        'target_vip': vip,
        'port': port,
        'duration_s': duration,
        'parallel_streams': parallel,
        'throughput_mbps': round(float(recv.get('bits_per_second', 0.0)) / 1_000_000.0, 2),
        'retransmits': sent.get('retransmits'),
        'raw': data,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vip', required=True)
    ap.add_argument('--port', type=int, default=5201)
    ap.add_argument('--duration', type=int, default=10)
    ap.add_argument('--parallel', type=int, default=1)
    ap.add_argument('--json', default=None)
    args = ap.parse_args()
    try:
        result = run_iperf3(args.vip, args.port, args.duration, args.parallel)
    except FileNotFoundError:
        print('iperf3 not found. Install with: sudo apt install iperf3', file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f'iperf3 error: {e}', file=sys.stderr)
        sys.exit(1)

    print('=== iperf3 Benchmark ===')
    print(f"Target VIP: {result['target_vip']}:{result['port']}")
    print(f"Duration: {result['duration_s']}s  Parallel streams: {result['parallel_streams']}")
    print(f"Throughput: {result['throughput_mbps']} Mbps")
    print(f"Retransmits: {result['retransmits']}")
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"JSON written: {args.json}")


if __name__ == '__main__':
    main()
