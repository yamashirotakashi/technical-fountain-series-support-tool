"""起動テストスクリプト"""
import sys
import os

# 依存関係のインポートテスト
print("依存関係をテストしています...")

try:
    print("1. PyQt5...")
    from PyQt6.QtWidgets import QApplication
    print("   ✓ PyQt5: OK")
except Exception as e:
    print(f"   ✗ PyQt5: {e}")
    sys.exit(1)

try:
    print("2. requests...")
    import requests
    print("   ✓ requests: OK")
except Exception as e:
    print(f"   ✗ requests: {e}")
    print("   urllib3のバージョンに問題がある可能性があります")
    print("   fix_dependencies.ps1を実行してください")
    sys.exit(1)

try:
    print("3. Google API...")
    import google.auth
    print("   ✓ Google API: OK")
except Exception as e:
    print(f"   ✗ Google API: {e}")

try:
    print("4. python-docx...")
    import docx
    print("   ✓ python-docx: OK")
except Exception as e:
    print(f"   ✗ python-docx: {e}")

try:
    print("5. dotenv...")
    from dotenv import load_dotenv
    print("   ✓ dotenv: OK")
except Exception as e:
    print(f"   ✗ dotenv: {e}")

print("\n基本的なインポートテスト...")

try:
    print("6. メインウィンドウ...")
    from gui.main_window import MainWindow
    print("   ✓ MainWindow: OK")
except Exception as e:
    print(f"   ✗ MainWindow: {e}")
    import traceback
    traceback.print_exc()

print("\nすべてのテストが完了しました。")
print("main.pyを実行してください。")