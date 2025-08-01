"""
インポートテストスクリプト
各モジュールが正しくインポートできるか確認
"""

import sys
import os

print("=== Import Test Script ===")
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")
print(f"Current Dir: {os.getcwd()}")
print()

# テストするモジュール
modules_to_test = [
    # 標準ライブラリ
    ("asyncio", "標準ライブラリ"),
    ("json", "標準ライブラリ"),
    ("pathlib", "標準ライブラリ"),
    
    # PyQt6
    ("PyQt6", "PyQt6本体"),
    ("PyQt6.QtCore", "PyQt6 Core"),
    ("PyQt6.QtWidgets", "PyQt6 Widgets"),
    ("PyQt6.QtGui", "PyQt6 GUI"),
    
    # 非同期関連
    ("qasync", "Qt非同期"),
    ("asyncqt", "Qt非同期（代替）"),
    ("aiohttp", "非同期HTTP"),
    
    # 外部API
    ("dotenv", "環境変数"),
    ("slack_sdk", "Slack SDK"),
    ("google.auth", "Google認証"),
    ("googleapiclient", "Google API"),
]

print("モジュールインポートテスト:")
print("-" * 50)

failed_imports = []

for module_name, description in modules_to_test:
    try:
        __import__(module_name)
        print(f"[OK] {module_name:<20} - {description}")
    except ImportError as e:
        print(f"[FAIL] {module_name:<20} - {description}")
        print(f"       エラー: {e}")
        failed_imports.append((module_name, str(e)))

print("-" * 50)

# アプリケーションモジュールのテスト
print("\nアプリケーションモジュールテスト:")
print("-" * 50)

app_modules = [
    "api_client",
    "slack_client", 
    "sheets_client",
    "config_manager",
    "main_window"
]

for module_name in app_modules:
    try:
        __import__(module_name)
        print(f"[OK] {module_name}")
    except ImportError as e:
        print(f"[FAIL] {module_name}")
        print(f"       エラー: {e}")
        failed_imports.append((module_name, str(e)))

print("-" * 50)

# 結果サマリー
if failed_imports:
    print(f"\n失敗したインポート: {len(failed_imports)}")
    for module, error in failed_imports:
        print(f"  - {module}: {error}")
else:
    print("\nすべてのモジュールが正常にインポートできました！")

# PyQt6の詳細情報
print("\nPyQt6詳細情報:")
try:
    from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
    print(f"  Qt Version: {QT_VERSION_STR}")
    print(f"  PyQt Version: {PYQT_VERSION_STR}")
except:
    print("  PyQt6のバージョン情報を取得できませんでした")

# 環境変数の確認
print("\n環境変数:")
print(f"  QT_PLUGIN_PATH: {os.environ.get('QT_PLUGIN_PATH', 'Not set')}")
print(f"  QT_QPA_PLATFORM_PLUGIN_PATH: {os.environ.get('QT_QPA_PLATFORM_PLUGIN_PATH', 'Not set')}")

input("\nPress Enter to exit...")