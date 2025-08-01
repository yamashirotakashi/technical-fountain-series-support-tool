"""
技術の泉シリーズプロジェクト初期化ツール - コンソール版エントリーポイント
GUI起動前の詳細なデバッグ情報を表示
"""

__version__ = "1.2-console"

import sys
import os
import traceback
from pathlib import Path

def main():
    """メインエントリーポイント"""
    print("=== PJinit Console Debug Version ===")
    print(f"Version: {__version__}")
    print(f"Python: {sys.version}")
    print(f"Executable: {sys.executable}")
    print(f"Frozen: {getattr(sys, 'frozen', False)}")
    print(f"Current Dir: {os.getcwd()}")
    print()
    
    # 実行環境の確認
    if getattr(sys, 'frozen', False):
        # EXE実行時
        exe_dir = Path(sys.executable).parent
        print(f"EXE Directory: {exe_dir}")
        print(f"_internal exists: {(exe_dir / '_internal').exists()}")
        print(f"config exists: {(exe_dir / 'config').exists()}")
        
        # sys.pathの確認
        print("\nsys.path:")
        for i, path in enumerate(sys.path[:5]):
            print(f"  [{i}] {path}")
    
    try:
        # 基本的なインポートテスト
        print("\n--- Import Test ---")
        
        # 1. 標準ライブラリ
        print("1. Standard libraries...")
        import asyncio
        import json
        import logging
        print("  [OK] Standard libraries")
        
        # 2. PyQt6のインポート
        print("2. PyQt6...")
        try:
            from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
            print(f"  [OK] PyQt6 - Qt {QT_VERSION_STR}, PyQt {PYQT_VERSION_STR}")
        except ImportError as e:
            print(f"  [FAIL] PyQt6: {e}")
            raise
        
        # 3. PyQt6.QtWidgets
        print("3. PyQt6.QtWidgets...")
        from PyQt6.QtWidgets import QApplication
        print("  [OK] PyQt6.QtWidgets")
        
        # 4. その他の依存関係
        print("4. Other dependencies...")
        import dotenv
        import aiohttp
        import slack_sdk
        print("  [OK] External dependencies")
        
        # 5. qasyncのインポート
        print("5. Qt async support...")
        try:
            import qasync
            print("  [OK] qasync")
        except ImportError:
            try:
                import asyncqt
                print("  [OK] asyncqt (alternative)")
            except ImportError as e:
                print(f"  [WARNING] No Qt async support: {e}")
        
        # 6. アプリケーションモジュール
        print("\n--- Application Modules ---")
        from main_window import main as gui_main
        print("  [OK] main_window imported")
        
        # GUI起動の確認
        print("\n--- Starting GUI ---")
        print("Launching GUI application...")
        
        # GUIを起動
        gui_main()
        
        print("\nGUI application exited normally")
        
    except Exception as e:
        print(f"\n--- ERROR ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        print(f"\nTraceback:")
        traceback.print_exc()
        
        # エラーをファイルに保存
        if getattr(sys, 'frozen', False):
            error_file = Path(sys.executable).parent / "error_log.txt"
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"PJinit Error Log\n")
                f.write(f"Version: {__version__}\n")
                f.write(f"Python: {sys.version}\n")
                f.write(f"Error: {e}\n\n")
                f.write(traceback.format_exc())
            print(f"\nError log saved to: {error_file}")
    
    finally:
        # EXE実行時は一時停止
        if getattr(sys, 'frozen', False):
            input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()