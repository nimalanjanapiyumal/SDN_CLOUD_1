from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

if __package__ is None or __package__ == '':
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, flash, redirect, render_template, request, url_for

from dashboard.services import ControllerApiClient, get_openstack_manager


app = Flask(__name__)
app.secret_key = os.getenv('DASHBOARD_SECRET_KEY', 'sdn-hybrid-dashboard')


def _load_controller_state() -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    client = ControllerApiClient()
    try:
        return client.status(), None
    except Exception as exc:
        return None, str(exc)


def _load_openstack_state() -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    if not os.getenv('OS_CLOUD'):
        return None, 'OS_CLOUD not set. OpenStack controls are disabled until clouds.yaml and OS_CLOUD are configured.'
    try:
        manager = get_openstack_manager()
        return {
            'servers': manager.list_servers(),
            'networks': manager.list_networks(),
            'floating_ips': manager.list_floating_ips(),
        }, None
    except Exception as exc:
        return None, str(exc)


@app.get('/')
def index():
    status, controller_error = _load_controller_state()
    openstack, openstack_error = _load_openstack_state()
    return render_template(
        'index.html',
        status=status,
        controller_error=controller_error,
        openstack=openstack,
        openstack_error=openstack_error,
    )


@app.post('/action/recompute')
def recompute():
    client = ControllerApiClient()
    try:
        payload = client.recompute()
        flash(f"GA recomputed successfully: {payload.get('weights', {})}", 'success')
    except Exception as exc:
        flash(f'GA recompute failed: {exc}', 'danger')
    return redirect(url_for('index'))


@app.post('/action/backend/<name>')
def set_backend_health(name: str):
    healthy = request.form.get('healthy') == '1'
    client = ControllerApiClient()
    try:
        client.set_health(name, healthy)
        flash(f'Backend {name} updated. healthy={healthy}', 'success')
    except Exception as exc:
        flash(f'Failed to update backend {name}: {exc}', 'danger')
    return redirect(url_for('index'))


@app.post('/action/scale')
def scale_openstack():
    action = request.form.get('action', 'out')
    role = request.form.get('role', 'backend')
    count = max(1, int(request.form.get('count', '1')))
    try:
        manager = get_openstack_manager()
        if action == 'out':
            created = manager.scale_out(count=count, role=role)
            flash(f'Scaled out {len(created)} OpenStack server(s).', 'success')
        else:
            prefix = f"{os.getenv('OS_MANAGED_PREFIX', 'hybrid-lb')}-{role}"
            deleted = manager.scale_in(count=count, prefix=prefix)
            flash(f'Scaled in {len(deleted)} OpenStack server(s): {deleted}', 'warning')
    except Exception as exc:
        flash(f'OpenStack action failed: {exc}', 'danger')
    return redirect(url_for('index'))


def main() -> None:
    host = os.getenv('DASHBOARD_HOST', '0.0.0.0')
    port = int(os.getenv('DASHBOARD_PORT', '5555'))
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    main()
