# -*- mode: python ; coding: utf-8 -*-
import sys

if sys.version_info.releaselevel != 'final' or not ((3, 10) <= sys.version_info[:2] <= (3, 13)):
    raise SystemExit(
        'Build Downloader Studio with CPython 3.10-3.13 final. '
        'Python 3.14/3.15 builds can fail at startup with python*.dll load errors.'
    )

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/downloader-studio-logo.ico'],
)
