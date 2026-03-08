
from __future__ import annotations
import json, os, time
from pathlib import Path
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

app = Flask(__name__)
app.secret_key = 'sdn-hybrid-lb'
BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / 'data'
DATA_DIR.mkdir(exist_ok=True)
OPENSTACK_CFG = DATA_DIR / 'openstack_env.json'
ENV_KEYS = ['OS_CLOUD','OS_AUTH_URL','OS_USERNAME','OS_PASSWORD','OS_PROJECT_NAME','OS_USER_DOMAIN_NAME','OS_PROJECT_DOMAIN_NAME']

def controller_url(path: str) -> str:
    base = os.environ.get('CONTROLLER_API_URL', 'http://127.0.0.1:8080').rstrip('/')
    return base + path

def get_status():
    try:
        r = requests.get(controller_url('/lb/status'), timeout=3)
        r.raise_for_status()
        data = r.json(); data['_ok'] = True; return data
    except Exception as e:
        return {'_ok': False, 'error': str(e), 'controller_runtime': {'datapaths_connected': 0, 'openflow_connected': False}, 'backends': [], 'weights': {}, 'active_flows': 0, 'vip': {'ip': '10.0.0.100'}}

def load_jsons(prefix: str):
    out=[]
    for p in sorted(DATA_DIR.glob(f'{prefix}_*.json')):
        try:
            out.append(json.loads(p.read_text(encoding='utf-8')))
        except Exception:
            pass
    return out

def load_openstack_cfg():
    if OPENSTACK_CFG.exists():
        try:
            data = json.loads(OPENSTACK_CFG.read_text(encoding='utf-8'))
            return {k: str(v) for k, v in data.items() if k in ENV_KEYS and v is not None}
        except Exception:
            return {}
    return {}

def save_openstack_cfg(data: dict):
    current = load_openstack_cfg()
    clean = dict(current)
    for k in ENV_KEYS:
        v = (data.get(k) or '').strip()
        if v:
            clean[k] = v
    # Allow explicit clear except defaults
    for k in ['OS_CLOUD','OS_AUTH_URL','OS_USERNAME','OS_PROJECT_NAME']:
        if data.get(k) == '':
            clean.pop(k, None)
    if data.get('OS_PASSWORD'):
        clean['OS_PASSWORD'] = data['OS_PASSWORD'].strip()
    if data.get('OS_USER_DOMAIN_NAME'):
        clean['OS_USER_DOMAIN_NAME'] = data['OS_USER_DOMAIN_NAME'].strip()
    else:
        clean['OS_USER_DOMAIN_NAME'] = 'Default'
    if data.get('OS_PROJECT_DOMAIN_NAME'):
        clean['OS_PROJECT_DOMAIN_NAME'] = data['OS_PROJECT_DOMAIN_NAME'].strip()
    else:
        clean['OS_PROJECT_DOMAIN_NAME'] = 'Default'
    if not clean:
        OPENSTACK_CFG.unlink(missing_ok=True)
    else:
        OPENSTACK_CFG.write_text(json.dumps(clean, indent=2), encoding='utf-8')

def effective_openstack_env():
    cfg = load_openstack_cfg()
    return {k: os.environ.get(k) or cfg.get(k, '') for k in ENV_KEYS}

def openstack_info():
    env = effective_openstack_env()
    present = {k: bool(env.get(k)) for k in ENV_KEYS}
    configured = bool(env.get('OS_CLOUD')) or all(env.get(k) for k in ['OS_AUTH_URL','OS_USERNAME','OS_PASSWORD','OS_PROJECT_NAME'])
    info = {'configured': configured, 'present': present, 'values': {k: ('********' if k == 'OS_PASSWORD' and env.get(k) else env.get(k, '')) for k in ENV_KEYS}, 'servers': [], 'error': None, 'source': 'saved dashboard config' if load_openstack_cfg() else 'process environment'}
    if not configured:
        info['error'] = 'OpenStack is not configured yet. Save OS_CLOUD or Keystone variables below.'
        return info
    try:
        import openstack
        if env.get('OS_CLOUD'):
            conn = openstack.connect(cloud=env['OS_CLOUD'])
        else:
            conn = openstack.connect(auth_url=env.get('OS_AUTH_URL'), username=env.get('OS_USERNAME'), password=env.get('OS_PASSWORD'), project_name=env.get('OS_PROJECT_NAME'), user_domain_name=env.get('OS_USER_DOMAIN_NAME') or 'Default', project_domain_name=env.get('OS_PROJECT_DOMAIN_NAME') or 'Default')
        for s in conn.compute.servers(details=True):
            addrs=[]
            for net, vals in (s.addresses or {}).items():
                for v in vals:
                    addrs.append(f"{net}: {v.get('addr')}")
            info['servers'].append({'name': s.name, 'status': s.status, 'addresses': ', '.join(addrs)})
    except Exception as e:
        info['error'] = str(e)
    return info

@app.route('/')
def overview(): return render_template('overview.html')

@app.route('/openstack')
def openstack_page(): return render_template('openstack.html', info=openstack_info())

@app.route('/testing')
def testing_page(): return render_template('testing.html', http_runs=load_jsons('http'), iperf_runs=load_jsons('iperf'))

@app.route('/api/status')
def api_status(): return jsonify(get_status())

@app.route('/api/recompute', methods=['POST'])
def api_recompute():
    try:
        r = requests.post(controller_url('/lb/recompute'), timeout=5)
        return (r.text, r.status_code, {'Content-Type': r.headers.get('Content-Type','application/json')})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/health/<name>', methods=['POST'])
def api_health(name):
    healthy = request.form.get('healthy','true').lower() == 'true'
    try:
        r = requests.post(controller_url(f'/lb/health/{name}'), json={'healthy': healthy}, timeout=5)
        return (r.text, r.status_code, {'Content-Type': r.headers.get('Content-Type','application/json')})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/openstack/save', methods=['POST'])
def openstack_save():
    payload = {k: request.form.get(k, '') for k in ENV_KEYS}
    save_openstack_cfg(payload)
    flash('OpenStack settings saved for the dashboard.', 'ok')
    return redirect(url_for('openstack_page'))

@app.route('/openstack/clear', methods=['POST'])
def openstack_clear():
    OPENSTACK_CFG.unlink(missing_ok=True)
    flash('Saved OpenStack settings cleared.', 'ok')
    return redirect(url_for('openstack_page'))

@app.route('/upload/<kind>', methods=['POST'])
def upload(kind):
    f = request.files.get('file')
    if not f: flash('No file uploaded', 'error'); return redirect(url_for('testing_page'))
    path = DATA_DIR / f'{kind}_{int(time.time())}.json'; path.write_bytes(f.read()); flash(f'Uploaded {path.name}', 'ok'); return redirect(url_for('testing_page'))

@app.route('/clear-results', methods=['POST'])
def clear_results():
    for p in DATA_DIR.glob('*.json'):
        if p.name != OPENSTACK_CFG.name:
            p.unlink(missing_ok=True)
    flash('Cleared uploaded benchmark results', 'ok'); return redirect(url_for('testing_page'))

if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=False)
