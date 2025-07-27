# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# プロジェクトのルートディレクトリ
ROOT_DIR = Path(SPECPATH)

# アプリケーション情報
APP_NAME = "TechZip1.0"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "技術の泉シリーズ制作支援ツール"
APP_ICON = None  # デフォルトアイコンを使用

# 分析設定
a = Analysis(
    ['main.py'],
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=[
        # 設定ファイル（デフォルト）
        ('config/settings.json', 'config'),
        # ドキュメント
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        # PyQt6関連
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        # Google API関連
        'google.auth',
        'google.auth.transport.requests',
        'google.oauth2',
        'google.oauth2.credentials',
        'google_auth_oauthlib',
        'google_auth_oauthlib.flow',
        'googleapiclient',
        'googleapiclient.discovery',
        'googleapiclient.errors',
        # その他の依存関係
        'requests',
        'urllib3',
        'docx',
        'dotenv',
        'selenium',
        'psutil',
        'bs4',
        # エンコーディング
        'encodings.utf_8',
        'encodings.ascii',
        'encodings.cp932',
        'encodings.shift_jis',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 不要なモジュール
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
        'test',
        'tests',
        'pytest',
        'pip',
        'setuptools',
        'wheel',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Gmail OAuth認証ファイルの処理
# 実行時に外部から読み込むため、dataには含めない
# ユーザーは初回実行時に認証を行う必要がある

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUIアプリケーションなのでコンソールは非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='resources/version_info.txt' if os.path.exists('resources/version_info.txt') else None,
    uac_admin=False,  # 管理者権限は不要
    icon=APP_ICON,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

# 単一ファイルEXE版（オプション）
# コメントアウトを外すと単一ファイルEXEも生成される
"""
exe_onefile = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=f'{APP_NAME}_portable',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=None,
    uac_admin=False,
    icon=APP_ICON,
)
"""