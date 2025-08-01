# -*- mode: python ; coding: utf-8 -*-
"""
技術の泉シリーズプロジェクト初期化ツール - PyInstaller設定ファイル
フォルダ方式での高速起動対応版
"""

import os
from pathlib import Path

# 基本パス設定
app_dir = Path('.')
config_dir = app_dir / 'config'

# 追加データファイル
added_files = []

# 設定ファイルがある場合は追加
if config_dir.exists():
    added_files.append((str(config_dir), 'config'))

# .envファイルがある場合は追加
env_file = app_dir / '.env'
if env_file.exists():
    added_files.append((str(env_file), '.'))

# PyQt6の必要なプラグイン
qt_plugins = [
    'platforms',
    'imageformats',
    'iconengines',
    'styles'
]

# 隠されたインポート（PyInstallerが自動検出できないモジュール）
hidden_imports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'qasync',
    'asyncqt',
    'aiohttp',
    'slack_sdk',
    'google.auth',
    'google.auth.transport.requests',
    'googleapiclient',
    'googleapiclient.discovery',
    'dotenv',
    'pathlib',
    'asyncio',
    'logging',
    'json',
    'base64',
    'datetime',
    'typing',
    'os',
    'sys'
]

# 除外するモジュール（サイズ削減）
excluded_modules = [
    'tkinter',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'PIL',
    'IPython',
    'jupyter',
    'notebook'
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
    excludes=excluded_modules,
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
    exclude_binaries=True,  # フォルダ方式のためTrue
    name='TechBridge_ProjectInitializer.exe',  # Windows用.exe拡張子
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 圧縮を有効化
    console=True,  # コンソール表示を有効化（デバッグ用）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',  # Windows 64bit用
    target_os='Windows',   # Windowsターゲット指定
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # アイコンファイルがあれば指定
    version_file=None  # バージョン情報ファイルがあれば指定
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TechBridge_ProjectInitializer'
)