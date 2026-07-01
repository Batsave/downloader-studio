#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON_BIN="./.venv-build/Scripts/python.exe"
INSTALL_DEPS=0
BUILD_ARGS=()

for arg in "$@"; do
  if [[ "$arg" == "--install-deps" ]]; then
    INSTALL_DEPS=1
  else
    BUILD_ARGS+=("$arg")
  fi
done

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Creating build venv with Python 3.13..."
  py -3.13 -m venv .venv-build
  INSTALL_DEPS=1
fi

echo "Using: $("$PYTHON_BIN" --version)"

if ! "$PYTHON_BIN" -c "import PyInstaller, PyQt5, yt_dlp, requests" >/dev/null 2>&1; then
  INSTALL_DEPS=1
fi

if [[ "$INSTALL_DEPS" == "1" ]]; then
  "$PYTHON_BIN" -m pip install --upgrade pip
  "$PYTHON_BIN" -m pip install -r requirements.txt pyinstaller
else
  echo "Dependencies already installed. Use --install-deps to refresh them."
fi

"$PYTHON_BIN" build_exe.py "${BUILD_ARGS[@]}"
