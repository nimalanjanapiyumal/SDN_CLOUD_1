#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, statistics, threading, time, urllib.request

def worker(url, stop_at, results, lock):
    while time.time() < stop_at:
        t0 = time.perf_counter(); ok = False; code = None
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                r.read(); code = r.getcode(); ok = 200 <= code < 300
        except Exception:
            ok = False
        dt = (time.perf_counter() - t0) * 1000.0
        with lock:
            results.append({'ok': ok, 'latency_ms': dt, 'code': code})

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--url', required=True); ap.add_argument('--concurrency', type=int, default=10); ap.add_argument('--duration', type=int, default=10); ap.add_argument('--sla-ms', type=float, default=200.0); ap.add_argument('--json', dest='json_path'); args = ap.parse_args()
    results=[]; lock=threading.Lock(); threads=[]; stop_at = time.time() + args.duration
    for _ in range(args.concurrency):
        t = threading.Thread(target=worker, args=(args.url, stop_at, results, lock), daemon=True); t.start(); threads.append(t)
    for t in threads: t.join()
    lat = [r['latency_ms'] for r in results]; oks = [r for r in results if r['ok']]
    out = {'url': args.url, 'concurrency': args.concurrency, 'duration': args.duration, 'requests_total': len(results), 'success_total': len(oks), 'error_total': len(results)-len(oks), 'error_rate_pct': round(((len(results)-len(oks))/max(1,len(results)))*100.0,2), 'req_per_sec': round(len(results)/max(1,args.duration),2), 'p50_ms': round(statistics.median(lat),2) if lat else None, 'p95_ms': round(sorted(lat)[max(0, int(len(lat)*0.95)-1)],2) if lat else None, 'sla_ms': args.sla_ms, 'sla_compliance_pct': round((sum(1 for x in lat if x <= args.sla_ms)/max(1,len(lat)))*100.0,2) if lat else 0.0, 'samples': results[:2000]}
    print(json.dumps(out, indent=2))
    if args.json_path:
        with open(args.json_path, 'w', encoding='utf-8') as f: json.dump(out, f, indent=2)

if __name__ == '__main__':
    main()
