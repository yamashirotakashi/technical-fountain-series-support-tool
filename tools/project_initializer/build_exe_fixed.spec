# -*- mode: python ; coding: utf-8 -*-
"""
技術の泉シリーズプロジェクト初期化ツール - PyInstaller設定ファイル（修正版）
python312.dllを確実に含める
"""

import os
import sys
from pathlib import Path

# 基本パス設定
app_dir = Path('.')
config_dir = app_dir / 'config'

# Python DLLの検索（バージョン自動判定）
import sys
python_version = f"{sys.version_info.major}{sys.version_info.minor}"
python_dll_name = f"python{python_version}.dll"
print(f"Looking for {python_dll_name} (Python {sys.version_info.major}.{sys.version_info.minor})")

python_dll = None
python_exe_dir = Path(sys.executable).parent

# まず実行中のPythonから探す
if (python_exe_dir / python_dll_name).exists():
    python_dll = str(python_exe_dir / python_dll_name)
elif (python_exe_dir.parent / python_dll_name).exists():
    python_dll = str(python_exe_dir.parent / python_dll_name)
else:
    # 一般的な場所を検索（バージョンに対応）
    search_paths = [
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs' / 'Python' / f'Python{python_version}',
        Path(f'C:/Users/tky99/AppData/Local/Programs/Python/Python{python_version}'),
        Path(f'C:/Python{python_version}'),
        Path(f'C:/Program Files/Python{python_version}'),
        Path(f'C:/Program Files (x86)/Python{python_version}'),
        # 仮想環境も検索
        Path('C:/Users/tky99/DEV/techbridge/app/mini_apps/project_initializer/venv_windows/Scripts'),
        Path('C:/Users/tky99/DEV/techbridge/app/mini_apps/project_initializer/venv_exe/Scripts'),
    ]
    for path in search_paths:
        if (path / python_dll_name).exists():
            python_dll = str(path / python_dll_name)
            break
        # Scriptsディレクトリの親も確認
        elif path.name == 'Scripts' and (path.parent / python_dll_name).exists():
            python_dll = str(path.parent / python_dll_name)
            break

# バイナリファイルリスト
binary_files = []
if python_dll:
    print(f"Found {python_dll_name} at: {python_dll}")
    binary_files.append((python_dll, '.'))
else:
    print(f"WARNING: {python_dll_name} not found!")
    # 警告を表示して、手動での追加を促す
    print(f"Please ensure {python_dll_name} is available in your Python installation.")
    print("The EXE may not work without it.")

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

# PyQt6のプラグインを確実に含める
try:
    import PyQt6
    qt_dir = Path(PyQt6.__file__).parent
    plugins_dir = qt_dir / 'Qt6' / 'plugins'
    if plugins_dir.exists():
        for plugin in qt_plugins:
            plugin_path = plugins_dir / plugin
            if plugin_path.exists():
                print(f"Including PyQt6 plugin: {plugin}")
except:
    pass

# 隠されたインポート（PyInstallerが自動検出できないモジュール）
hidden_imports = [
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
    pathex=[],
    binaries=binary_files,  # python312.dllを追加
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
    name='TechBridge_ProjectInitializer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 圧縮を有効化
    console=True,  # コンソール表示を有効化（デバッグ用）
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
    upx=True,
    upx_exclude=['python312.dll'],  # python312.dllは圧縮しない
    name='TechBridge_ProjectInitializer'
)