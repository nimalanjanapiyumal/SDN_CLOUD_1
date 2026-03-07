# Corrected build

This package fixes the controller startup error:

- `ModuleNotFoundError: No module named 'os_ken.cmd'`
- `AttributeError: module 'os_ken.base.app_manager' has no attribute 'RyuApp'`

Changes:
- controller uses local `launcher.py` instead of `python -m os_ken.cmd.manager`
- OS-Ken app now uses `app_manager.OSKenApp` when available and falls back to `app_manager.RyuApp`

Recommended run order:
```bash
cd /home/user/SDN_CLOUD_1
bash manage.sh fix-perms
bash manage.sh controller bootstrap
bash manage.sh controller start
bash manage.sh controller logs
```
