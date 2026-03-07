from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import os

import requests

from infra.openstack.openstack_manager import OpenStackManager


@dataclass
class ControllerApiClient:
    base_url: str = os.getenv('LB_CONTROLLER_URL', 'http://127.0.0.1:8080')
    timeout: float = float(os.getenv('LB_CONTROLLER_TIMEOUT', '3'))

    def _url(self, path: str) -> str:
        return self.base_url.rstrip('/') + path

    def status(self) -> Dict[str, Any]:
        resp = requests.get(self._url('/lb/status'), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def recompute(self) -> Dict[str, Any]:
        resp = requests.post(self._url('/lb/recompute'), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def set_health(self, name: str, healthy: bool) -> Dict[str, Any]:
        resp = requests.post(self._url(f'/lb/health/{name}'), json={'healthy': healthy}, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()


def get_openstack_manager() -> OpenStackManager:
    return OpenStackManager()
