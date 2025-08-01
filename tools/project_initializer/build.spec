# -*- mode: python ; coding: utf-8 -*-
"""
Project Initializer - PyInstaller Configuration
Standalone tool for TechBridge project initialization
"""

from pathlib import Path

# パス設定
app_dir = Path('.')

# データファイル
datas = []
if (app_dir / '.env').exists():
    datas.append(('.env', '.'))
if (app_dir / 'config').exists():
    datas.append(('config', 'config'))

# Analysis
a = Analysis(
    ['main_exe.py'],
    pathex=[str(app_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'qasync',
        'asyncqt',
        'aiohttp',
        'slack_sdk',
        'google.auth',
        'googleapiclient',
        'dotenv',
        # プロジェクトモジュール
        'main_window',
        'project_initializer',
        'google_sheets_reader',
        'slack_channel_creator',
        'github_repo_creator',
        'asyncqt_fixed'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas'],
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
    name='PJinit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
    target_os='Windows',
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PJinit'
)
