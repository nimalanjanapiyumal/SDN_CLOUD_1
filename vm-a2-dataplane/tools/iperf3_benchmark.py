#!/usr/bin/env python3
"""iperf3 benchmark helper (optional).

Example (in Mininet):
  # start iperf3 server on each backend:
  h2 iperf3 -s -p 5201 &
  h3 iperf3 -s -p 5201 &
  h4 iperf3 -s -p 5201 &

  # run client to VIP (controller will distribute flows)
  h1 python3 tools/iperf3_benchmark.py --vip 10.0.0.100 --port 5201 --duration 10 --parallel 5

Note: iperf3 must be installed.
"""

import argparse
import json
import subprocess
import sys


def run_iperf3(vip: str, port: int, duration: int, parallel: int) -> float:
    cmd = [
        "iperf3",
        "-c",
        vip,
        "-p",
        str(port),
        "-t",
        str(duration),
        "-P",
        str(parallel),
        "-J",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    data = json.loads(p.stdout)
    # bits_per_second from end.sum_received (or sum_sent)
    bps = float(data["end"]["sum_received"]["bits_per_second"])
    return bps / 1_000_000.0  # Mbps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vip", required=True)
    ap.add_argument("--port", type=int, default=5201)
    ap.add_argument("--duration", type=int, default=10)
    ap.add_argument("--parallel", type=int, default=1)
    args = ap.parse_args()

    try:
        mbps = run_iperf3(args.vip, args.port, args.duration, args.parallel)
    except FileNotFoundError:
        print("iperf3 not found. Install with: sudo apt install iperf3", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"iperf3 error: {e}", file=sys.stderr)
        sys.exit(1)

    print("=== iperf3 Benchmark ===")
    print(f"Target VIP: {args.vip}:{args.port}")
    print(f"Duration: {args.duration}s  Parallel streams: {args.parallel}")
    print(f"Throughput: {mbps:.2f} Mbps")


if __name__ == "__main__":
    main()
