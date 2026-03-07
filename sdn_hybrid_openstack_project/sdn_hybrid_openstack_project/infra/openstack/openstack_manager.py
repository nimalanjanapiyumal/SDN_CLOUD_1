from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os
import time


def _split_csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


@dataclass
class OpenStackSettings:
    cloud: Optional[str] = os.getenv('OS_CLOUD')
    image: Optional[str] = os.getenv('OS_IMAGE')
    flavor: Optional[str] = os.getenv('OS_FLAVOR')
    network: Optional[str] = os.getenv('OS_NETWORK')
    key_name: Optional[str] = os.getenv('OS_KEY_NAME')
    security_groups: List[str] = field(default_factory=lambda: _split_csv(os.getenv('OS_SECURITY_GROUPS')))
    managed_prefix: str = os.getenv('OS_MANAGED_PREFIX', 'hybrid-lb')
    external_network: Optional[str] = os.getenv('OS_EXTERNAL_NETWORK')
    availability_zone: Optional[str] = os.getenv('OS_AVAILABILITY_ZONE')
    wait: bool = os.getenv('OS_WAIT', 'false').lower() in {'1', 'true', 'yes'}

    @classmethod
    def from_env(cls) -> 'OpenStackSettings':
        return cls()


class OpenStackManager:
    def __init__(self, settings: Optional[OpenStackSettings] = None) -> None:
        self.settings = settings or OpenStackSettings.from_env()
        self.conn = self._connect()

    def _connect(self):
        try:
            import openstack  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                'openstacksdk is required. Install with: pip install openstacksdk'
            ) from e

        if not self.settings.cloud:
            raise RuntimeError('OS_CLOUD is not set. Configure clouds.yaml and export OS_CLOUD.')
        return openstack.connect(cloud=self.settings.cloud)  # type: ignore

    def _resolve_image(self, image: Optional[str] = None) -> str:
        target = image or self.settings.image
        if not target:
            raise ValueError('OpenStack image is not configured. Set OS_IMAGE or pass --image.')
        obj = self.conn.compute.find_image(target, ignore_missing=False)  # type: ignore
        return str(obj.id)

    def _resolve_flavor(self, flavor: Optional[str] = None) -> str:
        target = flavor or self.settings.flavor
        if not target:
            raise ValueError('OpenStack flavor is not configured. Set OS_FLAVOR or pass --flavor.')
        obj = self.conn.compute.find_flavor(target, ignore_missing=False)  # type: ignore
        return str(obj.id)

    def _resolve_network(self, network: Optional[str] = None) -> Optional[str]:
        target = network or self.settings.network
        if not target:
            return None
        obj = self.conn.network.find_network(target, ignore_missing=False)  # type: ignore
        return str(obj.id)

    def list_servers(self, prefix: Optional[str] = None) -> List[dict]:
        out = []
        for server in self.conn.compute.servers(details=True):  # type: ignore
            name = getattr(server, 'name', '')
            if prefix and not name.startswith(prefix):
                continue
            out.append({
                'id': str(server.id),
                'name': name,
                'status': getattr(server, 'status', ''),
                'addresses': getattr(server, 'addresses', {}) or {},
                'created_at': getattr(server, 'created_at', ''),
            })
        out.sort(key=lambda item: item.get('created_at', ''))
        return out

    def list_networks(self) -> List[dict]:
        out = []
        for network in self.conn.network.networks():  # type: ignore
            out.append({
                'id': str(network.id),
                'name': getattr(network, 'name', ''),
                'status': getattr(network, 'status', ''),
                'subnets': list(getattr(network, 'subnet_ids', []) or []),
            })
        out.sort(key=lambda item: item['name'])
        return out

    def list_floating_ips(self) -> List[dict]:
        out = []
        for ip in self.conn.network.ips():  # type: ignore
            out.append({
                'id': str(ip.id),
                'floating_ip_address': getattr(ip, 'floating_ip_address', ''),
                'status': getattr(ip, 'status', ''),
                'fixed_ip_address': getattr(ip, 'fixed_ip_address', ''),
            })
        out.sort(key=lambda item: item['floating_ip_address'])
        return out

    def create_server(
        self,
        name: str,
        image: Optional[str] = None,
        flavor: Optional[str] = None,
        network: Optional[str] = None,
        key_name: Optional[str] = None,
        security_groups: Optional[List[str]] = None,
        user_data: Optional[str] = None,
        auto_floating_ip: bool = False,
    ) -> dict:
        image_id = self._resolve_image(image)
        flavor_id = self._resolve_flavor(flavor)
        network_id = self._resolve_network(network)
        key = key_name or self.settings.key_name
        secgroups = security_groups if security_groups is not None else self.settings.security_groups

        server = self.conn.compute.create_server(  # type: ignore
            name=name,
            image_id=image_id,
            flavor_id=flavor_id,
            networks=[{'uuid': network_id}] if network_id else None,
            key_name=key,
            security_groups=secgroups or None,
            availability_zone=self.settings.availability_zone,
            user_data=user_data,
            metadata={'managed-by': 'sdn-hybrid-openstack-project'},
        )
        if self.settings.wait:
            server = self.conn.compute.wait_for_server(server)  # type: ignore

        if auto_floating_ip and self.settings.external_network:
            self._attach_floating_ip(server)

        return {
            'id': str(server.id),
            'name': getattr(server, 'name', name),
            'status': getattr(server, 'status', ''),
            'addresses': getattr(server, 'addresses', {}) or {},
        }

    def _attach_floating_ip(self, server) -> None:
        ext_net = self.conn.network.find_network(self.settings.external_network, ignore_missing=False)  # type: ignore
        fip = self.conn.network.create_ip(floating_network_id=ext_net.id)  # type: ignore
        self.conn.compute.add_floating_ip_to_server(server, fip.floating_ip_address)  # type: ignore

    def scale_out(self, count: int = 1, role: str = 'backend') -> List[dict]:
        created = []
        for i in range(int(count)):
            name = f"{self.settings.managed_prefix}-{role}-{int(time.time())}-{i}"
            created.append(self.create_server(name=name))
        return created

    def scale_in(self, count: int = 1, prefix: Optional[str] = None) -> List[str]:
        target_prefix = prefix or self.settings.managed_prefix
        servers = self.list_servers(prefix=target_prefix)
        deleted = []
        for server in servers[: int(count)]:
            self.conn.compute.delete_server(server['id'], ignore_missing=True)  # type: ignore
            deleted.append(server['name'])
        return deleted
