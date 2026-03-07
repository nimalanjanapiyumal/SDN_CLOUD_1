#!/usr/bin/env python3
"""Simple HTTP benchmark tool (standard library only).

Usage:
  python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 50 --duration 20 --sla-ms 200

Outputs:
  - req/s (throughput)
  - p50/p95 latency (ms)
  - error rate
  - SLA compliance (% under threshold)
"""

import argparse
import csv
import threading
import time
import urllib.request
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Result:
    ok: bool
    latency_ms: float


def percentile(data: List[float], p: float) -> Optional[float]:
    if not data:
        return None
    data = sorted(data)
    k = (len(data) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(data) - 1)
    if f == c:
        return data[f]
    return data[f] + (data[c] - data[f]) * (k - f)


def worker(url: str, timeout: float, stop_at: float, out: List[Result], lock: threading.Lock):
    while time.time() < stop_at:
        t0 = time.perf_counter()
        ok = True
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                resp.read(32)
        except Exception:
            ok = False
        t1 = time.perf_counter()
        with lock:
            out.append(Result(ok=ok, latency_ms=(t1 - t0) * 1000.0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--concurrency", type=int, default=20)
    ap.add_argument("--duration", type=int, default=10)
    ap.add_argument("--timeout", type=float, default=2.0)
    ap.add_argument("--sla-ms", type=float, default=200.0)
    ap.add_argument("--csv", default=None, help="Optional CSV output path")
    args = ap.parse_args()

    results: List[Result] = []
    lock = threading.Lock()

    stop_at = time.time() + args.duration
    threads = []
    for _ in range(args.concurrency):
        t = threading.Thread(target=worker, args=(args.url, args.timeout, stop_at, results, lock), daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    ok_lat = [r.latency_ms for r in results if r.ok]
    fail = [r for r in results if not r.ok]

    total = len(results)
    ok = len(ok_lat)
    fail_n = len(fail)

    p50 = percentile(ok_lat, 50) if ok_lat else None
    p95 = percentile(ok_lat, 95) if ok_lat else None

    req_per_s = total / max(1e-9, args.duration)
    err_rate = (fail_n / total * 100.0) if total else 0.0

    sla_ok = [x for x in ok_lat if x <= args.sla_ms]
    sla_pct = (len(sla_ok) / ok * 100.0) if ok else 0.0

    print("=== HTTP Benchmark ===")
    print(f"URL: {args.url}")
    print(f"Concurrency: {args.concurrency}  Duration: {args.duration}s")
    print(f"Total requests: {total}  Success: {ok}  Fail: {fail_n}  Error rate: {err_rate:.2f}%")
    print(f"Throughput: {req_per_s:.2f} req/s")
    if p50 is not None:
        print(f"Latency p50: {p50:.2f} ms")
    if p95 is not None:
        print(f"Latency p95: {p95:.2f} ms")
    print(f"SLA <= {args.sla_ms} ms: {sla_pct:.2f}% (success-only)")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ok", "latency_ms"])
            for r in results:
                w.writerow([int(r.ok), f"{r.latency_ms:.3f}"])
        print(f"CSV written: {args.csv}")


if __name__ == "__main__":
    main()
