
#!/usr/bin/env bash
set -euo pipefail

VENV_PATH="${1:-.venv-controller}"
RYU_SRC_DIR="${RYU_SRC_DIR:-}"
WORK_DIR="${WORK_DIR:-/tmp/ryu-build}"

if [[ ! -d "$VENV_PATH" ]]; then
  echo "[ERROR] Virtualenv not found: $VENV_PATH" >&2
  exit 1
fi

source "$VENV_PATH/bin/activate"
python -m pip install --upgrade pip wheel setuptools packaging
mkdir -p "$WORK_DIR"

if [[ -n "$RYU_SRC_DIR" ]]; then
  SRC="$RYU_SRC_DIR"
else
  SRC="$WORK_DIR/ryu"
  rm -rf "$SRC"
  echo "[INFO] Cloning Ryu source..."
  git clone --depth 1 https://github.com/faucetsdn/ryu.git "$SRC"
fi

echo "[INFO] Patching Ryu hooks.py for modern setuptools..."
python - "$SRC" <<'PY2'
from pathlib import Path
import sys
src = Path(sys.argv[1])
hooks = src / 'ryu' / 'hooks.py'
text = hooks.read_text(encoding='utf-8')
old = '_main_module()._orig_get_script_args = easy_install.get_script_args'
new = '_main_module()._orig_get_script_args = getattr(easy_install, "get_script_args", None)'
if old in text:
    text = text.replace(old, new)
    hooks.write_text(text, encoding='utf-8')
    print('[OK] Patched hooks.py')
else:
    print('[INFO] hooks.py already patched or line not present')
PY2

echo "[INFO] Installing patched Ryu in legacy mode..."
python -m pip install --no-build-isolation --no-use-pep517 "$SRC"
python - <<'PY2'
import importlib
m = importlib.import_module('ryu')
print('[OK] Ryu import succeeded:', getattr(m, '__file__', 'unknown'))
PY2
