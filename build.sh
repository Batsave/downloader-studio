#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON_BIN="./.venv-build/Scripts/python.exe"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Creating build venv with Python 3.13..."
  py -3.13 -m venv .venv-build
fi

echo "Using: $("$PYTHON_BIN" --version)"

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install -r requirements.txt pyinstaller
"$PYTHON_BIN" build_exe.py "$@"
