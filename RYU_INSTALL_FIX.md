
# Ryu installation fix included in this package

## Problem
Installing upstream Ryu directly with `pip install ryu` or `pip install git+https://github.com/faucetsdn/ryu.git` can fail on Python 3.10+ because `ryu/hooks.py` references `easy_install.get_script_args`, which modern setuptools no longer exposes. The upstream issue list still shows this installation error open.

## What this package does
The script `scripts/install_ryu_patched.sh`:
1. clones the Ryu source from GitHub,
2. patches the offending `ryu/hooks.py` line,
3. installs Ryu with `--no-build-isolation --no-use-pep517`.

## If GitHub access is blocked in your lab
You can still use the same script with a pre-downloaded Ryu source tree by placing it at:
`third_party/ryu-src`

Then run:
```bash
RYU_SRC_DIR=third_party/ryu-src bash scripts/install_ryu_patched.sh .venv-controller
```
