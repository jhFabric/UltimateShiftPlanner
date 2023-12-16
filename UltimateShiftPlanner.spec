# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['UltimateShiftPlanner.py'],
    pathex=[],
    binaries=[],
    datas=[('resources/source', 'resources/source'), ('resources/keys', 'resources/keys'), ('resources/data', 'resources/data'), ('tmp', 'tmp'), ('output', 'output')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='UltimateShiftPlanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
