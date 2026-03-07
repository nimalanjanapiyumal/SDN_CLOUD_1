#!/usr/bin/env bash
set -euo pipefail

VENV_PATH="${1:-.venv-controller}"
RYU_SRC_DIR="${RYU_SRC_DIR:-}"
WORK_DIR="${WORK_DIR:-/tmp/ryu-build}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -d "$VENV_PATH" ]]; then
  echo "[ERROR] Virtualenv not found: $VENV_PATH" >&2
  exit 1
fi

source "$VENV_PATH/bin/activate"

echo "[INFO] Pinning Python build toolchain for legacy Ryu install..."
python -m pip install --upgrade 'pip==24.3.1'
python -m pip uninstall -y setuptools packaging wheel pbr >/dev/null 2>&1 || true
python -m pip install   'setuptools==68.2.2'   'wheel==0.45.1'   'packaging==24.2'   'pbr==6.1.1'
python "$ROOT_DIR/scripts/check_build_toolchain.py"

mkdir -p "$WORK_DIR"

if [[ -n "$RYU_SRC_DIR" ]]; then
  SRC="$RYU_SRC_DIR"
elif [[ -d "$ROOT_DIR/vendor/ryu" ]]; then
  SRC="$ROOT_DIR/vendor/ryu"
  echo "[INFO] Using bundled Ryu source at: $SRC"
else
  SRC="$WORK_DIR/ryu"
  rm -rf "$SRC"
  echo "[INFO] Cloning Ryu source..."
  git clone --depth 1 https://github.com/faucetsdn/ryu.git "$SRC"
fi

echo "[INFO] Patching Ryu hooks.py and setup.cfg for modern packaging..."
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

setupcfg = src / 'setup.cfg'
if setupcfg.exists():
    cfg = setupcfg.read_text(encoding='utf-8')
    replacements = {
        'author-email': 'author_email',
        'home-page': 'home_page',
        'description-file': 'description_file',
        '
Release =': '
release =',
        '
Group =': '
group =',
        '
Requires =': '
requires =',
    }
    changed = False
    for a, b in replacements.items():
        if a in cfg:
            cfg = cfg.replace(a, b)
            changed = True
    if changed:
        setupcfg.write_text(cfg, encoding='utf-8')
        print('[OK] Normalized setup.cfg compatibility keys')
    else:
        print('[INFO] setup.cfg compatibility keys already normalized')

pyproject = src / 'pyproject.toml'
pyproject.write_text("""[build-system]
requires = ["setuptools==68.2.2", "wheel==0.45.1", "packaging==24.2", "pbr==6.1.1"]
build-backend = "setuptools.build_meta"
""", encoding='utf-8')
print('[OK] Wrote pyproject.toml with pinned build requirements')
PY2

echo "[INFO] Installing bundled Ryu dependency files first..."
for req in "$SRC/requirements.txt" "$SRC/tools/pip-requires" "$SRC/tools/optional-requires"; do
  if [[ -f "$req" ]]; then
    echo "[INFO] Installing dependencies from: $req"
    python -m pip install -r "$req" || true
  fi
done

echo "[INFO] Installing patched Ryu..."
if PIP_NO_BUILD_ISOLATION=1 python -m pip install "$SRC"; then
  echo "[OK] Ryu installed via pip local source"
else
  echo "[WARN] pip local install failed, falling back to setup.py install"
  (cd "$SRC" && python setup.py install)
fi

python - <<'PY2'
import importlib
m = importlib.import_module('ryu')
print('[OK] Ryu import succeeded:', getattr(m, '__file__', 'unknown'))
PY2
