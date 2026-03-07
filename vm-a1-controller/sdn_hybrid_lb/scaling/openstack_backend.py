from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time


@dataclass
class OpenStackScaleConfig:
    cloud: Optional[str] = None
    image: Optional[str] = None
    flavor: Optional[str] = None
    network: Optional[str] = None
    key_name: Optional[str] = None
    security_groups: List[str] = field(default_factory=list)
    name_prefix: str = "hybrid-lb-srv"
    metadata: Dict[str, str] = field(default_factory=lambda: {"managed-by": "sdn-hybrid-lb"})
    min_servers: int = 1
    wait: bool = False


class OpenStackScalerBackend:
    """Simple OpenStack scaler using openstacksdk.

    This is intentionally generic so it can be reused by the dashboard,
    experiments, or future autoscaling hooks.
    """

    def __init__(self, cfg: OpenStackScaleConfig) -> None:
        self.cfg = cfg
        try:
            import openstack  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "openstacksdk is required for OpenStack scaling. Install with: pip install openstacksdk"
            ) from e
        self.conn = openstack.connect(cloud=cfg.cloud)  # type: ignore

    def _resolve_image(self) -> str:
        image = self.conn.compute.find_image(self.cfg.image, ignore_missing=False)  # type: ignore
        return str(image.id)

    def _resolve_flavor(self) -> str:
        flavor = self.conn.compute.find_flavor(self.cfg.flavor, ignore_missing=False)  # type: ignore
        return str(flavor.id)

    def _resolve_network(self) -> Optional[str]:
        if not self.cfg.network:
            return None
        network = self.conn.network.find_network(self.cfg.network, ignore_missing=False)  # type: ignore
        return str(network.id)

    def list_managed_servers(self):
        servers = list(self.conn.compute.servers(details=True))  # type: ignore
        prefix = self.cfg.name_prefix
        managed = [s for s in servers if getattr(s, 'name', '').startswith(prefix)]
        managed.sort(key=lambda s: getattr(s, 'created_at', '') or '')
        return managed

    def scale_out(self, count: int = 1) -> None:
        image_id = self._resolve_image()
        flavor_id = self._resolve_flavor()
        network_id = self._resolve_network()

        for i in range(int(count)):
            name = f"{self.cfg.name_prefix}-{int(time.time())}-{i}"
            server = self.conn.compute.create_server(  # type: ignore
                name=name,
                image_id=image_id,
                flavor_id=flavor_id,
                networks=[{"uuid": network_id}] if network_id else None,
                key_name=self.cfg.key_name,
                security_groups=self.cfg.security_groups or None,
                metadata=self.cfg.metadata or None,
            )
            if self.cfg.wait:
                self.conn.compute.wait_for_server(server)  # type: ignore

    def scale_in(self, count: int = 1) -> None:
        managed = self.list_managed_servers()
        removable = max(0, len(managed) - int(self.cfg.min_servers))
        if removable <= 0:
            return

        for server in managed[: min(int(count), removable)]:
            self.conn.compute.delete_server(server.id, ignore_missing=True)  # type: ignore
