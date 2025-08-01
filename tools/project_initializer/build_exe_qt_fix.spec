# -*- mode: python ; coding: utf-8 -*-
"""
技術の泉シリーズプロジェクト初期化ツール - PyInstaller設定ファイル（Qt修正版）
PyQt6プラットフォームプラグインを確実に含める
"""

import os
import sys
from pathlib import Path

# PyQt6のインストール場所を探す
def find_pyqt6_dir():
    try:
        import PyQt6
        return Path(PyQt6.__file__).parent
    except:
        return None

# 基本パス設定
app_dir = Path('.')
config_dir = app_dir / 'config'
pyqt6_dir = find_pyqt6_dir()

# 追加データファイル
added_files = []

# 設定ファイルがある場合は追加
if config_dir.exists():
    added_files.append((str(config_dir), 'config'))

# .envファイルがある場合は追加
env_file = app_dir / '.env'
if env_file.exists():
    added_files.append((str(env_file), '.'))

# PyQt6プラグインを明示的に追加
if pyqt6_dir:
    qt6_dir = pyqt6_dir / 'Qt6'
    if qt6_dir.exists():
        # プラットフォームプラグイン（必須）
        platforms_dir = qt6_dir / 'plugins' / 'platforms'
        if platforms_dir.exists():
            added_files.append((str(platforms_dir), 'PyQt6/Qt6/plugins/platforms'))
            print(f"Adding platforms plugins from: {platforms_dir}")
        
        # その他のプラグイン
        for plugin_type in ['imageformats', 'iconengines', 'styles']:
            plugin_dir = qt6_dir / 'plugins' / plugin_type
            if plugin_dir.exists():
                added_files.append((str(plugin_dir), f'PyQt6/Qt6/plugins/{plugin_type}'))
                print(f"Adding {plugin_type} plugins from: {plugin_dir}")
        
        # binディレクトリのDLL
        bin_dir = qt6_dir / 'bin'
        if bin_dir.exists():
            # 必要なQt DLLのみを選択的に追加
            qt_dlls = [
                'Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll',
                'Qt6Network.dll', 'Qt6Svg.dll'
            ]
            for dll in qt_dlls:
                dll_path = bin_dir / dll
                if dll_path.exists():
                    added_files.append((str(dll_path), '.'))
                    print(f"Adding Qt DLL: {dll}")

# 隠されたインポート（PyInstallerが自動検出できないモジュール）
hidden_imports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.sip',
    'qasync',
    'asyncqt',
    'aiohttp',
    'slack_sdk',
    'slack_sdk.web',
    'slack_sdk.web.async_client',
    'google.auth',
    'google.auth.transport.requests',
    'google.oauth2',
    'google.oauth2.service_account',
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
    pathex=[str(app_dir)],
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
    exclude_binaries=True,
    name='TechBridge_ProjectInitializer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX圧縮を無効化（Qt問題回避）
    console=True,  # コンソール表示（デバッグ用）
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