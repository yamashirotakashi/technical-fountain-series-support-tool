"""
技術の泉シリーズプロジェクト初期化ツール - デバッグ版
エラーログをファイルに出力
"""

__version__ = "1.2-debug"

import sys
import os
import traceback
from pathlib import Path
from datetime import datetime

# ログファイルのパス設定
if getattr(sys, 'frozen', False):
    log_dir = Path(sys.executable).parent / "logs"
else:
    log_dir = Path(__file__).parent / "logs"

log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"pjinit_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def debug_log(message):
    """デバッグログを出力"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}\n"
    
    # ファイルに書き込み
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_message)
    
    # コンソールにも出力
    print(log_message.strip())

def main():
    """メインエントリーポイント"""
    debug_log("=== PJinit Debug Start ===")
    debug_log(f"Version: {__version__}")
    debug_log(f"Python: {sys.version}")
    debug_log(f"Executable: {sys.executable}")
    debug_log(f"Frozen: {getattr(sys, 'frozen', False)}")
    debug_log(f"Current Dir: {os.getcwd()}")
    debug_log(f"Log File: {log_file}")
    
    try:
        # 環境情報の記録
        debug_log("\n--- Environment ---")
        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).parent
            debug_log(f"EXE Dir: {exe_dir}")
            debug_log(f"_internal exists: {(exe_dir / '_internal').exists()}")
            debug_log(f"config exists: {(exe_dir / 'config').exists()}")
        
        # sys.pathの確認
        debug_log("\n--- Python Path ---")
        for i, path in enumerate(sys.path[:5]):
            debug_log(f"sys.path[{i}]: {path}")
        
        # 必要なモジュールのインポートテスト
        debug_log("\n--- Import Test ---")
        
        # 標準ライブラリ
        try:
            import asyncio
            debug_log("asyncio: OK")
        except Exception as e:
            debug_log(f"asyncio: ERROR - {e}")
        
        # PyQt6
        try:
            from PyQt6.QtCore import QT_VERSION_STR
            debug_log(f"PyQt6.QtCore: OK (Qt {QT_VERSION_STR})")
        except Exception as e:
            debug_log(f"PyQt6.QtCore: ERROR - {e}")
        
        try:
            from PyQt6.QtWidgets import QApplication
            debug_log("PyQt6.QtWidgets: OK")
        except Exception as e:
            debug_log(f"PyQt6.QtWidgets: ERROR - {e}")
        
        # その他の依存関係
        try:
            import dotenv
            debug_log("dotenv: OK")
        except Exception as e:
            debug_log(f"dotenv: ERROR - {e}")
        
        try:
            import aiohttp
            debug_log("aiohttp: OK")
        except Exception as e:
            debug_log(f"aiohttp: ERROR - {e}")
        
        try:
            import slack_sdk
            debug_log("slack_sdk: OK")
        except Exception as e:
            debug_log(f"slack_sdk: ERROR - {e}")
        
        # main_windowのインポート
        debug_log("\n--- Main Window Import ---")
        try:
            from main_window import main
            debug_log("main_window: OK")
            
            # GUIの起動
            debug_log("\n--- Starting GUI ---")
            main()
            debug_log("GUI exited normally")
            
        except Exception as e:
            debug_log(f"main_window: ERROR - {e}")
            debug_log(f"Traceback:\n{traceback.format_exc()}")
        
    except Exception as e:
        debug_log(f"\n--- FATAL ERROR ---")
        debug_log(f"Error: {e}")
        debug_log(f"Traceback:\n{traceback.format_exc()}")
    
    finally:
        debug_log("\n=== PJinit Debug End ===")
        debug_log(f"Log saved to: {log_file}")
        
        # EXE実行時はログファイルの場所を表示して一時停止
        if getattr(sys, 'frozen', False):
            print(f"\nログファイル: {log_file}")
            input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()