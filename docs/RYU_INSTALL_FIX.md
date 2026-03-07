# Ryu Install Fix

This package avoids the Python 3.10+ setuptools build failure by installing Ryu through:
- `scripts/install_ryu_patched.sh`
- controller-only bootstrap path

The dashboard environment does **not** install Ryu.

If you extracted from ZIP and got `Permission denied`, run:
```bash
bash manage.sh fix-perms
```

Direct controller run also works with:
```bash
cd vm-a1-controller
bash ./run_controller.sh
```
