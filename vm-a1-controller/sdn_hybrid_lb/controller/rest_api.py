from __future__ import annotations

import json
from ryu.app.wsgi import ControllerBase, route
from webob import Response


def _json_response(payload, status=200):
    body = json.dumps(payload, indent=2).encode('utf-8')
    return Response(status=status, content_type='application/json', charset='utf-8', body=body)


class LBRestController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super().__init__(req, link, data, **config)
        self.app = data['app']

    @route('lb', '/lb/status', methods=['GET'])
    def status(self, req, **kwargs):
        return _json_response(self.app.status())

    @route('lb', '/lb/recompute', methods=['POST'])
    def recompute(self, req, **kwargs):
        weights = self.app.lb.force_ga()
        return _json_response({'ok': True, 'weights': weights, 'status': self.app.status()})

    @route('lb', '/lb/health/{name}', methods=['POST'])
    def set_health(self, req, **kwargs):
        name = kwargs.get('name')
        try:
            payload = req.json_body if req.body else {}
        except Exception:
            payload = {}
        healthy = bool(payload.get('healthy', True))
        ok = self.app.lb.set_backend_health(name, healthy)
        return _json_response({'ok': ok, 'name': name, 'healthy': healthy, 'status': self.app.status()})
