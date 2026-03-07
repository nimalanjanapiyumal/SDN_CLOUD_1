#!/usr/bin/env python3
"""Simple HTTP benchmark tool (standard library only)."""

import argparse
import csv
import json
import threading
import time
import urllib.request
from dataclasses import dataclass, asdict
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
                resp.read(64)
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
    ap.add_argument("--csv", default=None)
    ap.add_argument("--json", default=None)
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
    total = len(results)
    ok = len(ok_lat)
    fail_n = total - ok
    p50 = percentile(ok_lat, 50) if ok_lat else None
    p95 = percentile(ok_lat, 95) if ok_lat else None
    req_per_s = total / max(1e-9, args.duration)
    err_rate = (fail_n / total * 100.0) if total else 0.0
    sla_ok = [x for x in ok_lat if x <= args.sla_ms]
    sla_pct = (len(sla_ok) / ok * 100.0) if ok else 0.0
    summary = {
        'url': args.url,
        'concurrency': args.concurrency,
        'duration_s': args.duration,
        'total_requests': total,
        'successful_requests': ok,
        'failed_requests': fail_n,
        'error_rate_pct': round(err_rate, 2),
        'throughput_req_per_s': round(req_per_s, 2),
        'latency_p50_ms': round(p50, 2) if p50 is not None else None,
        'latency_p95_ms': round(p95, 2) if p95 is not None else None,
        'sla_threshold_ms': args.sla_ms,
        'sla_compliance_pct': round(sla_pct, 2),
    }

    print("=== HTTP Benchmark ===")
    for k, v in summary.items():
        print(f"{k}: {v}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ok", "latency_ms"])
            for r in results:
                w.writerow([int(r.ok), f"{r.latency_ms:.3f}"])
        print(f"CSV written: {args.csv}")

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump({'summary': summary, 'samples': [asdict(r) for r in results]}, f, indent=2)
        print(f"JSON written: {args.json}")


if __name__ == "__main__":
    main()
