# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\modules\\techbook27_analyzer\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('app', 'app')],
    hiddenimports=['PyQt6', 'PyQt6.QtCore', 'PyQt6.QtWidgets', 'PyQt6.QtGui', 'PIL', 'PIL.Image', 'docx', 'openpyxl', 'logging.handlers', 'pathlib', 'datetime', 'threading', 'queue', 'app.modules.techbook27_analyzer', 'app.modules.techbook27_analyzer.ui', 'app.modules.techbook27_analyzer.core', 'app.modules.techbook27_analyzer.processors', 'app.modules.techbook27_analyzer.utils'],
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
    [],
    exclude_binaries=True,
    name='TechDisposal.1.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TechDisposal.1.0',
)
