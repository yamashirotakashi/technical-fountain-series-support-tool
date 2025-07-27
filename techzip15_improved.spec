# -*- mode: python ; coding: utf-8 -*-
"""
改善されたPyInstaller spec設定
- 環境変数とパス解決システム対応
- ランタイムフック追加
- 必要なデータファイルの包含
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 設定ファイルとテンプレート
        ('config', 'config'),
        # .env.templateは後で作成される
        
        # ドキュメント（存在する場合のみ）
        # README.mdやdocsは後で個別に確認
        
        # Gmail OAuth認証ファイル（存在する場合のみ）
        # ビルド時に動的に追加
    ],
    hiddenimports=[
        # PyQt6関連
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        
        # API関連
        'requests',
        'google.oauth2',
        'google.auth',
        'googleapiclient',
        'googleapiclient.discovery',
        'googleapiclient.errors',
        'googleapiclient.http',
        'google_auth_httplib2',
        'httplib2',
        
        # ファイル処理
        'docx',
        'python-docx',
        'zipfile',
        
        # 環境変数
        'dotenv',
        'python-dotenv',
        
        # Slack統合
        'slack_sdk',
        'slack_sdk.web',
        'slack_sdk.errors',
        
        # 暗号化
        'cryptography',
        'cryptography.fernet',
        
        # ログ
        'logging.handlers',
        
        # 追加モジュール
        'utils.path_resolver',
        'utils.env_manager',
        'core.gmail_oauth_exe_helper',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook_enhanced.py'],  # 拡張版ランタイムフック
    excludes=[
        'PyQt5',  # PyQt5を除外（PyQt6を使用）
        'PySide6',  # PySide6を除外
        'matplotlib',  # 使用していない場合
        'numpy',  # 使用していない場合
        'pandas',  # 使用していない場合
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 動的にファイルを追加
import os
from pathlib import Path

# Gmail OAuth認証ファイルの確認と追加
gmail_creds_path = Path('config/gmail_oauth_credentials.json')
if gmail_creds_path.exists():
    a.datas.append(('config/gmail_oauth_credentials.json', str(gmail_creds_path), 'DATA'))
    print(f"[OK] Gmail OAuth認証ファイルを追加: {gmail_creds_path}")
else:
    print("[WARNING] Gmail OAuth認証ファイルが見つかりません。Gmail API機能は制限されます。")

# README.mdの確認と追加
readme_path = Path('README.md')
if readme_path.exists():
    a.datas.append(('README.md', str(readme_path), 'DATA'))

# .env.templateの確認と追加
env_template_path = Path('.env.template')
if env_template_path.exists():
    a.datas.append(('.env.template', str(env_template_path), 'DATA'))

# Google Sheets認証ファイルの確認（パスは設定ファイルで指定）
# ユーザーが個別に配置する必要があるため、ここでは追加しない

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TECHZIP1.5',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # コンソールウィンドウなし
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # アイコンファイルがある場合は指定
    version_file=None,  # バージョン情報ファイルがある場合は指定
)