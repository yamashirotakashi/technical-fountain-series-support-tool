# -*- mode: python ; coding: utf-8 -*-
"""
TechBridge Project Initializer - Windows EXE専用PyInstaller設定
フォルダ方式、Windows専用最適化版
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
    'github_client',
    'path_resolver'
]

# Windows専用 - 隠されたインポート
hidden_imports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
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
    'sys'
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
python_files = ['main_exe.py']

# アプリケーション関連ファイルが存在する場合は追加
for module in app_modules:
    py_file = f"{module}.py"
    if (app_dir / py_file).exists():
        python_files.append(py_file)
        print(f"Adding module: {py_file}")
    else:
        print(f"Warning: {py_file} not found")

a = Analysis(
    python_files,
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

# バージョン情報を取得
def get_version():
    try:
        with open('main_exe.py', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
        return "1.0"
    except:
        return "1.0"

app_version = get_version()

# Windows EXE専用設定
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,         # フォルダ方式
    name=f'PJinit.{app_version}',  # バージョン付きファイル名
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                      # 圧縮有効
    console=True,                  # コンソール表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,              # アーキテクチャ自動検出
    codesign_identity=None,
    entitlements_file=None,
    icon=None,                     # アイコンファイルがあれば指定
    version_file=None,             # バージョン情報ファイルがあれば指定
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=f'PJinit.{app_version}'
)