"""インポートのみのテスト - GUI表示なし"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """必要なモジュールのインポートテスト"""
    print("モジュールインポートテスト開始...")
    
    try:
        # 標準ライブラリ
        print("1. 標準ライブラリ...")
        import threading
        import queue
        import time
        import json
        import tempfile
        import zipfile
        print("   ✓ 標準ライブラリ正常")
        
        # サードパーティライブラリ
        print("2. サードパーティライブラリ...")
        import requests
        print("   ✓ requests")
        
        import psutil
        print("   ✓ psutil")
        
        from dotenv import load_dotenv
        print("   ✓ python-dotenv")
        
        # プロジェクトモジュール
        print("3. プロジェクトモジュール...")
        try:
            from core.preflight.unified_preflight_manager import create_preflight_manager
            print("   ✓ unified_preflight_manager")
        except ImportError as e:
            print(f"   ✗ unified_preflight_manager: {e}")
            raise
        
        try:
            from core.preflight.verification_strategy import VerificationMode
            print("   ✓ verification_strategy")
        except ImportError as e:
            print(f"   ✗ verification_strategy: {e}")
            raise
        
        try:
            from core.preflight.job_state_manager import JobStatus, JobPriority
            print("   ✓ job_state_manager")
        except ImportError as e:
            print(f"   ✗ job_state_manager: {e}")
            raise
        
        try:
            from utils.logger import get_logger
            print("   ✓ logger")
        except ImportError as e:
            print(f"   ✗ logger: {e}")
            raise
        
        try:
            from tests.test_windows_powershell import WindowsPowerShellTestSuite
            print("   ✓ test_windows_powershell")
        except ImportError as e:
            print(f"   ✗ test_windows_powershell: {e}")
            raise
        
        # GUI関連（インポートのみ、初期化しない）
        print("4. GUIモジュール...")
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox, scrolledtext
        print("   ✓ tkinter関連")
        
        # 最後にGUIクラスのインポート
        try:
            from gui.integrated_test_gui import IntegratedTestGUI, TestResult, LogHandler
            print("   ✓ integrated_test_gui")
        except ImportError as e:
            print(f"   ✗ integrated_test_gui: {e}")
            raise
        
        print("\n🎉 すべてのインポートが成功しました！")
        return True
        
    except ImportError as e:
        print(f"\n❌ インポートエラー: {e}")
        print("必要な依存関係をインストールしてください:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment():
    """環境設定確認"""
    print("\n環境設定確認...")
    
    try:
        # .envファイル確認
        env_file = project_root / ".env"
        if env_file.exists():
            print("✓ .envファイル存在")
        else:
            print("⚠ .envファイルなし（テスト用ダミー設定を使用）")
        
        # 必要なディレクトリ確認
        required_dirs = ['gui', 'core', 'tests', 'utils']
        for dir_name in required_dirs:
            if (project_root / dir_name).exists():
                print(f"✓ {dir_name}ディレクトリ存在")
            else:
                print(f"✗ {dir_name}ディレクトリ不足")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ 環境設定エラー: {e}")
        return False

if __name__ == "__main__":
    print("TechZip Pre-flight Checker - インポート確認テスト")
    print("=" * 60)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_environment():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 準備完了！GUIアプリケーションを起動できます。")
        print("\n実行方法:")
        print("  Windows PowerShell: .\\run_gui.ps1")
        print("  コマンドプロンプト: run_gui.bat")
        print("  Python直接実行: python main_gui.py")
    else:
        print("❌ セットアップが不完全です。エラーを修正してください。")