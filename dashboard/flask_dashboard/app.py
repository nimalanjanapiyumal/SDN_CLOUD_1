
from __future__ import annotations

import os
from typing import Any, Dict, List

import requests
from flask import Flask, jsonify, redirect, render_template, request

try:
    import openstack  # type: ignore
except Exception:
    openstack = None

app = Flask(__name__)
CONTROLLER_API_URL = os.environ.get('CONTROLLER_API_URL', 'http://127.0.0.1:8080').rstrip('/')
OS_CLOUD = os.environ.get('OS_CLOUD')


def controller_get(path: str) -> Dict[str, Any]:
    r = requests.get(f"{CONTROLLER_API_URL}{path}", timeout=5)
    r.raise_for_status()
    return r.json()


def controller_post(path: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    r = requests.post(f"{CONTROLLER_API_URL}{path}", json=payload or {}, timeout=5)
    r.raise_for_status()
    return r.json()


def list_openstack_servers() -> List[Dict[str, Any]]:
    if openstack is None:
        return [{"name": "openstacksdk not installed", "status": "unavailable"}]
    try:
        conn = openstack.connect(cloud=OS_CLOUD) if OS_CLOUD else openstack.connect()
        out = []
        for s in conn.compute.servers():
            out.append({"name": s.name, "status": getattr(s, 'status', 'UNKNOWN')})
        return out
    except Exception as e:
        return [{"name": "openstack connection error", "status": str(e)}]


@app.route('/')
def index():
    status = {}
    error = None
    try:
        status = controller_get('/lb/status')
    except Exception as exc:
        error = str(exc)
    servers = list_openstack_servers()
    return render_template('index.html', controller=status, servers=servers, error=error, api_url=CONTROLLER_API_URL)


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
