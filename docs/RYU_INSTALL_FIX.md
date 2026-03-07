# Ryu Install Fix

This package fixes the Python 3.10+ Ryu install failure in two ways:

1. `scripts/install_ryu_patched.sh` patches `ryu/hooks.py` for modern `setuptools`.
2. The installer no longer uses the unsupported pip flag `--no-use-pep517`.
   It now tries:
   - `python -m pip install --no-build-isolation <local_ryu_source>`
   - and falls back to `python setup.py install` if needed.

The dashboard environment does **not** install Ryu.

Useful commands:
```bash
bash manage.sh controller bootstrap
bash manage.sh controller start
bash manage.sh controller logs
```
