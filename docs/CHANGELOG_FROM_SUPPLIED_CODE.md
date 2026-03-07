
# Changes made to the supplied code bundle

## Dependency and deployment fixes
- Split controller and dashboard environments so dashboard setup no longer installs Ryu.
- Added `scripts/install_ryu_patched.sh` to automate the Ryu source patch and install on Python 3.10+.
- Added three bootstrap scripts for controller, dashboard, and dataplane VMs.

## Controller logic fixes
- Added `capacity.max_connections` to backend models.
- Changed overload gating from `active_connections / max_observed_connections` to `active_connections / backend.capacity.max_connections`.
- Updated controller config to include `max_connections` for backends.

## Added components
- Flask operator dashboard.
- Prometheus example config.
- Grafana example dashboard JSON.
- Smoke tests.
- Direct deployment documentation.
