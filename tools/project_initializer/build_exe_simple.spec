# -*- mode: python ; coding: utf-8 -*-
"""
技術の泉シリーズプロジェクト初期化ツール - PyInstaller設定ファイル（シンプル版）
最小限の設定でpython312.dll問題を解決
"""

import os
import sys
from pathlib import Path

# 基本パス設定
app_dir = Path('.')
config_dir = app_dir / 'config'

# 追加データファイル
added_files = []
if config_dir.exists():
    added_files.append((str(config_dir), 'config'))

# 隠されたインポート（最小限）
hidden_imports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'qasync',
    'aiohttp',
    'slack_sdk',
    'google.auth',
    'googleapiclient',
    'dotenv',
]

a = Analysis(
    ['main_exe.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TechBridge_ProjectInitializer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX圧縮を無効化
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # UPX圧縮を無効化
    upx_exclude=[],
    name='TechBridge_ProjectInitializer'
)