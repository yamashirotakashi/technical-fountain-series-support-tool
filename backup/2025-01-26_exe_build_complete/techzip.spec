# -*- mode: python ; coding: utf-8 -*-
# 技術の泉シリーズ制作支援ツール - PyInstaller設定

import sys
from pathlib import Path

# プロジェクトのベースディレクトリ
import os
BASE_DIR = Path(os.getcwd())

# アイコンファイル（存在する場合）
ICON_FILE = BASE_DIR / 'assets' / 'icon.ico' if (BASE_DIR / 'assets' / 'icon.ico').exists() else None

a = Analysis(
    ['main.py'],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=[
        ('config', 'config'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'google.auth',
        'google.oauth2',
        'google.auth.transport.requests',
        'googleapiclient',
        'googleapiclient.discovery',
        'googleapiclient.errors',
        'certifi',
        'charset_normalizer',
        'idna',
        'requests',
        'urllib3',
        'dotenv',
        'colorama',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt5',  # PyQt5を除外
        'PySide2',
        'PySide6',
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TechZip',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUIアプリケーションなのでコンソールは非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON_FILE) if ICON_FILE else None,
)

# 追加の設定情報をコメントとして記載
"""
ビルドコマンド:
    pyinstaller techzip.spec

または、初回ビルド時:
    pyinstaller --onefile --windowed --name TechZip main.py

ビルド後の確認:
    1. dist/TechZip.exe が作成されていることを確認
    2. configフォルダがexeと同じディレクトリに必要
    3. .envファイルを配置（必要に応じて）
"""