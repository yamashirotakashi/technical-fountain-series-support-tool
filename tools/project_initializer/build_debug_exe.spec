# -*- mode: python ; coding: utf-8 -*-
"""
TechBridge Project Initializer - デバッグ版Windows EXE設定
詳細なエラー表示とコンソール出力付き
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

# アプリケーション関連ファイルの明示的追加
app_modules = [
    'main_window',
    'slack_client',
    'google_sheets',
    'github_client'
]

# Windows専用 - 隠されたインポート（デバッグ用）
hidden_imports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtApplication',
    'qasync',
    'asyncqt',
    'aiohttp',
    'aiohttp.client',
    'aiohttp.connector',
    'slack_sdk',
    'slack_sdk.web',
    'slack_sdk.web.client',
    'google.auth',
    'google.auth.transport.requests',
    'googleapiclient',
    'googleapiclient.discovery',
    'python_dotenv',
    'dotenv',
    'pathlib',
    'asyncio',
    'asyncio.events',
    'asyncio.base_events',
    'logging',
    'logging.handlers',
    'json',
    'base64',
    'datetime',
    'typing',
    'os',
    'sys',
    'traceback',
    'time'
] + app_modules

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
    'notebook',
    # Linux専用モジュールを除外
    'pwd',
    'grp',
    'resource',
    'termios'
]

# 必要なPythonファイルを明示的に指定
python_files = ['main_exe_debug.py']

# アプリケーション関連ファイルが存在する場合は追加
for module in app_modules:
    py_file = f"{module}.py"
    if (app_dir / py_file).exists():
        python_files.append(py_file)
        print(f"Adding module: {py_file}")
    else:
        print(f"Warning: {py_file} not found")

a = Analysis(
    python_files,  # デバッグ版エントリーポイント + 関連モジュール
    pathex=[str(app_dir)],  # 現在のディレクトリをパスに追加
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

# デバッグ版Windows EXE設定
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,         # フォルダ方式
    name='TechBridge_ProjectInitializer_Debug',  # デバッグ版識別用
    debug=True,                    # デバッグモード有効
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                     # 圧縮無効（デバッグ用）
    console=True,                  # コンソール表示（必須）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,                     # 圧縮無効（デバッグ用）
    upx_exclude=[],
    name='TechBridge_ProjectInitializer_Debug'
)