#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import time
from typing import Any, Dict

import requests
from prometheus_client import Gauge, start_http_server


LOG = logging.getLogger('controller_exporter')

CONTROLLER_UP = Gauge('sdn_hybrid_lb_controller_up', 'Controller status API reachability')
ACTIVE_FLOWS = Gauge('sdn_hybrid_lb_active_flows', 'Number of active LB flows')
BACKEND_HEALTH = Gauge('sdn_hybrid_lb_backend_health', 'Backend health state', ['backend'])
BACKEND_WEIGHT = Gauge('sdn_hybrid_lb_backend_weight', 'Current backend weight', ['backend'])
BACKEND_CPU = Gauge('sdn_hybrid_lb_backend_cpu_util', 'Backend CPU utilization', ['backend'])
BACKEND_MEM = Gauge('sdn_hybrid_lb_backend_mem_util', 'Backend memory utilization', ['backend'])
BACKEND_BW = Gauge('sdn_hybrid_lb_backend_bw_util', 'Backend bandwidth utilization', ['backend'])
BACKEND_CONN = Gauge('sdn_hybrid_lb_backend_active_connections', 'Backend active connections', ['backend'])
BACKEND_CONN_UTIL = Gauge('sdn_hybrid_lb_backend_connection_util', 'Backend connection utilization', ['backend'])
BACKEND_LAT = Gauge('sdn_hybrid_lb_backend_latency_ms', 'Backend latency in milliseconds', ['backend'])
BACKEND_TPUT = Gauge('sdn_hybrid_lb_backend_throughput_mbps', 'Backend throughput in Mbps', ['backend'])


def apply_status(status: Dict[str, Any]) -> None:
    ACTIVE_FLOWS.set(float(status.get('active_flows', 0)))
    weights = status.get('weights', {}) or {}
    for backend in status.get('backends', []) or []:
        name = str(backend.get('name'))
        metrics = backend.get('metrics', {}) or {}
        BACKEND_HEALTH.labels(backend=name).set(1.0 if backend.get('healthy') else 0.0)
        BACKEND_WEIGHT.labels(backend=name).set(float(weights.get(name, 0.0)))
        BACKEND_CPU.labels(backend=name).set(float(metrics.get('cpu_util') or 0.0))
        BACKEND_MEM.labels(backend=name).set(float(metrics.get('mem_util') or 0.0))
        BACKEND_BW.labels(backend=name).set(float(metrics.get('bw_util') or 0.0))
        BACKEND_CONN.labels(backend=name).set(float(metrics.get('active_connections') or 0.0))
        BACKEND_CONN_UTIL.labels(backend=name).set(float(backend.get('connection_util') or 0.0))
        BACKEND_LAT.labels(backend=name).set(float(metrics.get('latency_ms') or 0.0))
        BACKEND_TPUT.labels(backend=name).set(float(metrics.get('throughput_mbps') or 0.0))


def fetch_status(controller_url: str, timeout: float) -> Dict[str, Any]:
    resp = requests.get(controller_url.rstrip('/') + '/lb/status', timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    ap = argparse.ArgumentParser(description='Prometheus exporter for the SDN hybrid controller.')
    ap.add_argument('--controller-url', default='http://127.0.0.1:8080')
    ap.add_argument('--listen-host', default='0.0.0.0')
    ap.add_argument('--listen-port', type=int, default=9108)
    ap.add_argument('--interval', type=float, default=5.0)
    ap.add_argument('--timeout', type=float, default=3.0)
    ap.add_argument('--log-level', default='INFO')
    args = ap.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    start_http_server(args.listen_port, addr=args.listen_host)
    LOG.info('Exporter listening on %s:%s', args.listen_host, args.listen_port)

    while True:
        try:
            status = fetch_status(args.controller_url, timeout=args.timeout)
            apply_status(status)
            CONTROLLER_UP.set(1.0)
        except Exception as exc:
            CONTROLLER_UP.set(0.0)
            LOG.warning('Failed to poll controller: %s', exc)
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
