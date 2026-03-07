# Ryu Install Fix

This package pins a known-good Python packaging toolchain before installing Ryu:

- `pip==24.3.1`
- `setuptools==68.2.2`
- `wheel==0.45.1`
- `packaging==24.2`
- `pbr==6.1.1`

Why this is required:
- Ryu still uses legacy setup hooks.
- Newer `setuptools` releases can trigger `canonicalize_version(..., strip_trailing_zero=False)` build failures when paired with mismatched packaging internals.
- Constraining `setuptools` below 71 and keeping `packaging` modern avoids that failure path.

The installer also:
- patches `ryu/hooks.py`
- normalizes several old `setup.cfg` keys
- writes a local `pyproject.toml` with pinned build requirements
- falls back to `python setup.py install` if local pip install fails

Controller bootstrap already applies this automatically.
