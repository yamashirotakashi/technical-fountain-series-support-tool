# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# プロジェクトルートディレクトリ
project_root = Path.cwd()

block_cipher = None

a = Analysis(
    # メインスクリプト（GUI版）
    ['main_gui.py'],
    
    # 追加パス
    pathex=[str(project_root)],
    
    # バイナリファイル（必要に応じて）
    binaries=[],
    
    # データファイル（設定ファイル、リソースなど）
    datas=[
        ('config', 'config'),
        ('utils', 'utils'),
        ('core', 'core'),
        ('gui', 'gui'),
        ('tests', 'tests'),
        ('.env', '.'),
        ('requirements.txt', '.'),
    ],
    
    # 隠れたインポート（PyInstallerが自動検出できないモジュール）
    hiddenimports=[
        'dotenv',
        'requests',
        'psutil',
        'beautifulsoup4',
        'lxml',
        'email.mime.multipart',
        'email.mime.text',
        'imaplib',
        'smtplib',
        'json',
        'pathlib',
        'dataclasses',
        'typing',
        'asyncio',
        'concurrent.futures',
        'threading',
        'queue',
        'time',
        'datetime',
        'tempfile',
        'zipfile',
        'logging',
        # tkinter関連（GUI用）
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        # テストスイート関連
        'tests.test_windows_powershell',
        'core.preflight.unified_preflight_manager',
        'core.preflight.verification_strategy',
        'core.preflight.job_state_manager',
        'utils.logger',
    ],
    
    # 除外するモジュール
    excludes=[
        'PyQt6',
        'PyQt5',
        'matplotlib',
        'numpy',
        'pandas',
    ],
    
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TechZipPreflightCheckerGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # UPX圧縮を有効化（ファイルサイズ削減）
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowsアプリケーション（コンソール非表示）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
    version_file='version_info.txt' if os.path.exists('version_info.txt') else None,
)