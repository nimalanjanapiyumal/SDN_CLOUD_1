# Security Controls

## Infrastructure controls
- OpenStack security groups restrict inbound access.
- Separate private VM network for controller ↔ data plane traffic.
- SSH key-based access recommended.

## Host-level controls
If UFW is enabled on the controller VM:
```bash
sudo ufw allow 22/tcp
sudo ufw allow 6633/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 5555/tcp
sudo ufw allow 9108/tcp
```

## Application controls
- Existing flows remain sticky.
- New flows are blocked from overloaded or unhealthy backends.
- Backend health can be disabled manually for isolation/fault tests.
- Monitoring visibility supports anomaly and SLA detection.

## Credential handling
- Do not commit real OpenStack passwords or tokens.
- Use `clouds.yaml` or environment variables.
- Keep `clouds.yaml` in `~/.config/openstack/` on each VM.
