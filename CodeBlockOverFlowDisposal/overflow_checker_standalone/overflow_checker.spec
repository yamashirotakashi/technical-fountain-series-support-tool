# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller スペックファイル - 溢れチェッカー独立版
Windows EXE化用設定
"""

import sys
import os
from pathlib import Path

# アプリケーションのルートディレクトリ
ROOT_DIR = Path('.').resolve()
sys.path.insert(0, str(ROOT_DIR))

block_cipher = None

# データファイルとアセット
datas = []

# プロジェクトソースファイルを明示的に追加
project_modules = [
    ('core', 'core'),
    ('gui', 'gui'), 
    ('utils', 'utils')
]

for src, dst in project_modules:
    if os.path.exists(src):
        datas.append((src, dst))

# 設定ファイル（存在する場合のみ）
if os.path.exists('data'):
    datas.append(('data', 'data'))

# アセット（存在する場合のみ）
if os.path.exists('assets'):
    datas.append(('assets', 'assets'))

# バイナリファイル（オプション）
binaries = []

# 隠されたインポート（PyInstallerが自動検出できないモジュール）
hiddenimports = [
    # PyQt6関連
    'PyQt6.QtCore',
    'PyQt6.QtWidgets', 
    'PyQt6.QtGui',
    'PyQt6.sip',
    
    # PDF処理
    'fitz',  # PyMuPDF
    'pdfplumber',
    'pypdfium2',
    'pypdf',
    'PyPDF2',
    
    # 画像処理・OCR
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'cv2',
    'numpy',
    'pytesseract',
    
    # データベース
    'sqlite3',
    
    # ユーティリティ
    'packaging',
    'charset_normalizer',
    'cryptography',
    
    # Windows固有
    'win32api',
    'win32con',
    'win32gui',
    'pywintypes',
    
    # プロジェクト固有モジュール（すべて追加）
    'core',
    'core.pdf_processor',
    'core.learning_manager',
    'gui',
    'gui.main_window',
    'gui.result_dialog',
    'utils',
    'utils.logging_config',
    'utils.tesseract_config',
    'utils.windows_utils',
]

# 除外するモジュール（サイズ削減）
excludes = [
    # 不要な大型ライブラリ
    'matplotlib',
    'scipy',
    'pandas',
    'tensorflow',
    'torch',
    'jupyter',
    'notebook',
    
    # 開発ツール
    'pytest',
    'setuptools',
    'distutils',
    
    # 他のGUIフレームワーク
    'tkinter',
    'wx',
    
    # 不要なバックエンド
    'IPython',
]

# PyInstallerの解析設定
a = Analysis(
    ['run_ultimate.py'],
    pathex=[str(ROOT_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZアーカイブ作成
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE実行ファイル作成（フォルダ構成最適化）
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # フォルダ構成（高速起動）
    name='OverflowChecker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX圧縮無効（起動速度最優先）
    console=False,  # コンソールウィンドウ非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/overflow_checker.ico' if os.path.exists('assets/overflow_checker.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
    # 高速起動のための追加設定
    runtime_tmpdir=None,  # 一時ディレクトリ設定なし（高速化）
)

# 配布用フォルダ作成（高速起動最適化）
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,  # 高速起動を優先
    upx=False,    # 圧縮無効（起動速度最優先）
    upx_exclude=[],
    name='OverflowChecker',
    distpath='dist'
)

# Windows固有の設定
if sys.platform == 'win32':
    # アプリケーション情報
    app = BUNDLE(
        coll,
        name='OverflowChecker.app',
        bundle_identifier='com.claudecode.overflowchecker',
        version='1.0.0',
    ) if sys.platform == 'darwin' else None