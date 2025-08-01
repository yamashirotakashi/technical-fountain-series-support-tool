#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Windows PowerShell起動テスト"""

import sys
import os
from pathlib import Path

print("=" * 50)
print("Windows PowerShell起動テスト")
print("=" * 50)

# 1. Python環境確認
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Current working directory: {os.getcwd()}")

# 2. プロジェクトルート確認
project_root = Path(__file__).parent
print(f"Project root: {project_root}")
print(f"Project root exists: {project_root.exists()}")

# 3. sys.pathにプロジェクトルートを追加
sys.path.insert(0, str(project_root))
print(f"Updated sys.path: {sys.path[:3]}...")

# 4. 重要なファイルの存在確認
important_files = [
    '.env',
    'requirements.txt',
    'main.py',
    'utils/env_manager.py',
    'utils/path_resolver.py',
    'gui/main_window.py'
]

print("\n重要ファイルの存在確認:")
for file_path in important_files:
    full_path = project_root / file_path
    exists = full_path.exists()
    print(f"  {file_path}: {'✓' if exists else '✗'}")

# 5. .envファイル内容確認
env_file = project_root / '.env'
if env_file.exists():
    print(f"\n.envファイル内容確認:")
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:5], 1):  # 最初の5行のみ表示
                # 機密情報をマスク
                if '=' in line and any(secret in line.lower() for secret in ['password', 'token', 'key']):
                    key, _ = line.split('=', 1)
                    print(f"  {i}: {key}=***MASKED***")
                else:
                    print(f"  {i}: {line.strip()}")
    except Exception as e:
        print(f"  エラー: {e}")

# 6. モジュールインポートテスト
print("\nモジュールインポートテスト:")
test_modules = [
    'PyQt6',
    'PyQt6.QtWidgets',
    'PyQt6.QtCore'
]

for module in test_modules:
    try:
        __import__(module)
        print(f"  {module}: ✓")
    except ImportError as e:
        print(f"  {module}: ✗ ({e})")

# 7. カスタムモジュールインポートテスト
print("\nカスタムモジュールインポートテスト:")
custom_modules = [
    'utils.env_manager',
    'utils.path_resolver',
    'utils.config'
]

for module in custom_modules:
    try:
        __import__(module)
        print(f"  {module}: ✓")
    except ImportError as e:
        print(f"  {module}: ✗ ({e})")

# 8. 環境変数初期化テスト
print("\n環境変数初期化テスト:")
try:
    from utils.env_manager import EnvManager
    EnvManager.initialize()
    print("  環境変数初期化: ✓")
except Exception as e:
    print(f"  環境変数初期化: ✗ ({e})")

# 9. GUI初期化テスト（実際には表示しない）
print("\nGUI初期化テスト:")
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    
    # アプリケーションインスタンス作成（表示はしない）
    app = QApplication([])
    print("  QApplication作成: ✓")
    
    # メインウィンドウインポートテスト
    from gui.main_window import MainWindow
    print("  MainWindowインポート: ✓")
    
    app.quit()
    
except Exception as e:
    print(f"  GUI初期化: ✗ ({e})")

print("\n" + "=" * 50)
print("テスト完了")
print("=" * 50)