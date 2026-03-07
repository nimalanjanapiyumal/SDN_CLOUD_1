from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import requests
from flask import Flask, jsonify, redirect, render_template, request

try:
    import openstack  # type: ignore
except Exception:
    openstack = None

app = Flask(__name__)
CONTROLLER_API_URL = os.environ.get("CONTROLLER_API_URL", "http://127.0.0.1:8080").rstrip("/")
OS_CLOUD = os.environ.get("OS_CLOUD")
OPENSTACK_ENABLED = os.environ.get("OPENSTACK_ENABLED", "true").lower() == "true"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def controller_get(path: str) -> Dict[str, Any]:
    r = requests.get(f"{CONTROLLER_API_URL}{path}", timeout=5)
    r.raise_for_status()
    return r.json()


def controller_post(path: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    r = requests.post(f"{CONTROLLER_API_URL}{path}", json=payload or {}, timeout=5)
    r.raise_for_status()
    return r.json()


def _openstack_env_present() -> bool:
    keys = ["OS_AUTH_URL", "OS_USERNAME", "OS_PASSWORD", "OS_PROJECT_NAME"]
    return all(os.environ.get(k) for k in keys)


def _openstack_connect():
    if openstack is None:
        raise RuntimeError("openstacksdk not installed in dashboard environment")
    if not OPENSTACK_ENABLED:
        raise RuntimeError("OpenStack integration disabled by OPENSTACK_ENABLED=false")
    if OS_CLOUD:
        return openstack.connect(cloud=OS_CLOUD)
    if _openstack_env_present():
        return openstack.connect(cloud="envvars")
    raise RuntimeError(
        "OpenStack is not configured. Set OS_CLOUD with clouds.yaml or export OS_AUTH_URL, OS_USERNAME, OS_PASSWORD, OS_PROJECT_NAME and OS_USER_DOMAIN_NAME / OS_PROJECT_DOMAIN_NAME."
    )


def get_openstack_status() -> Tuple[str, List[Dict[str, Any]], str | None]:
    if openstack is None:
        return "sdk-missing", [], "Install openstacksdk in the dashboard venv."
    try:
        conn = _openstack_connect()
        servers = []
        for s in conn.compute.servers():
            addresses = []
            for net, entries in getattr(s, 'addresses', {}).items():
                for e in entries:
                    addr = e.get('addr')
                    if addr:
                        addresses.append(f"{net}:{addr}")
            servers.append({
                'name': s.name,
                'status': getattr(s, 'status', 'UNKNOWN'),
                'flavor': getattr(getattr(s, 'flavor', None), 'get', lambda x, d=None: d)('original_name', '') if getattr(s, 'flavor', None) else '',
                'addresses': ', '.join(addresses) or '-',
            })
        return "connected", servers, None
    except Exception as e:
        msg = str(e)
        if 'auth_url' in msg:
            return "not-configured", [], (
                "OpenStack credentials are missing. The dashboard needs OS_CLOUD pointing to a clouds.yaml profile, or OS_AUTH_URL / OS_USERNAME / OS_PASSWORD / OS_PROJECT_NAME environment variables."
            )
        return "error", [], msg


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def summarise_controller(status: Dict[str, Any]) -> Dict[str, Any]:
    backends = status.get('backends', []) or []
    healthy = sum(1 for b in backends if b.get('healthy'))
    unhealthy = len(backends) - healthy
    active_flows = int(status.get('active_flows', 0) or 0)
    rr_mode = (status.get('controller') or {}).get('rr_mode', 'n/a')
    total_thr = sum(_num((b.get('metrics') or {}).get('throughput_mbps')) for b in backends)
    avg_cpu = sum(_num((b.get('metrics') or {}).get('cpu_util')) for b in backends) / len(backends) if backends else 0.0
    avg_mem = sum(_num((b.get('metrics') or {}).get('mem_util')) for b in backends) / len(backends) if backends else 0.0
    avg_bw = sum(_num((b.get('metrics') or {}).get('bw_util')) for b in backends) / len(backends) if backends else 0.0
    return {
        'backend_count': len(backends),
        'healthy_count': healthy,
        'unhealthy_count': unhealthy,
        'active_flows': active_flows,
        'rr_mode': rr_mode,
        'total_throughput_mbps': round(total_thr, 2),
        'avg_cpu_util_pct': round(avg_cpu * 100.0, 1),
        'avg_mem_util_pct': round(avg_mem * 100.0, 1),
        'avg_bw_util_pct': round(avg_bw * 100.0, 1),
    }


def get_testing_plan() -> List[Dict[str, str]]:
    return [
        {
            'name': 'Functional integration',
            'goal': 'Verify controller, Mininet, VIP ARP, backend health toggle, and GA recompute.',
            'command': 'In Mininet: h1 ping -c 2 10.0.0.100; h1 curl http://10.0.0.100:8000',
            'metrics': 'Controller up, VIP reachable, JSON response shows backend name, flow count increments.'
        },
        {
            'name': 'Performance and scalability',
            'goal': 'Measure latency, throughput, errors, and SLA compliance under increasing concurrency.',
            'command': 'h1 python3 tools/http_benchmark.py --url http://10.0.0.100:8000 --concurrency 20 --duration 20 --sla-ms 200 --json /tmp/http_20.json',
            'metrics': 'req/s, p50, p95, error %, SLA <= 200 ms, active flows.'
        },
        {
            'name': 'Traffic throughput',
            'goal': 'Measure network throughput with iperf3 against the VIP.',
            'command': 'h1 python3 tools/iperf3_benchmark.py --vip 10.0.0.100 --port 5201 --duration 15 --parallel 4 --json /tmp/iperf.json',
            'metrics': 'Mbps, retransmits if available, parallel stream behavior.'
        },
        {
            'name': 'Fault tolerance',
            'goal': 'Simulate backend failure and verify traffic shifts to healthy nodes.',
            'command': 'Use dashboard health toggle or POST /lb/health/srv1 {"healthy": false}, then repeat curl/benchmark.',
            'metrics': 'Requests continue via remaining nodes, minimal error spike, backend health reflected in dashboard.'
        },
    ]


@app.route('/')
def index():
    status: Dict[str, Any] = {}
    error = None
    try:
        status = controller_get('/lb/status')
    except Exception as exc:
        error = str(exc)
    summary = summarise_controller(status) if status else {}
    os_state, servers, os_message = get_openstack_status()
    return render_template(
        'index.html',
        controller=status,
        summary=summary,
        servers=servers,
        error=error,
        api_url=CONTROLLER_API_URL,
        openstack_state=os_state,
        openstack_message=os_message,
        testing_plan=get_testing_plan(),
        generated_at=now_iso(),
    )


@app.post('/recompute')
def recompute():
    controller_post('/lb/recompute', {})
    return redirect('/')


@app.post('/backend/<name>/health')
def backend_health(name: str):
    healthy = request.form.get('healthy', 'true').lower() == 'true'
    controller_post(f'/lb/health/{name}', {'healthy': healthy})
    return redirect('/')


@app.get('/api/status')
def api_status():
    return jsonify(controller_get('/lb/status'))


@app.get('/api/openstack')
def api_openstack():
    state, servers, message = get_openstack_status()
    return jsonify({'state': state, 'servers': servers, 'message': message})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
