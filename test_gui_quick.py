"""統合テストGUIの簡単動作確認
GUIコンポーネントの基本的な初期化テスト
"""
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gui_import():
    """GUIモジュールのインポートテスト"""
    try:
        print("tkinterのインポートテスト...")
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog, scrolledtext
        print("✓ tkinter関連モジュール正常")
        
        print("プロジェクトモジュールのインポートテスト...")
        from gui.integrated_test_gui import IntegratedTestGUI, TestResult, LogHandler
        print("✓ 統合テストGUIモジュール正常")
        
        from tests.test_windows_powershell import WindowsPowerShellTestSuite
        print("✓ テストスイートモジュール正常")
        
        return True
    except ImportError as e:
        print(f"✗ インポートエラー: {e}")
        return False
    except Exception as e:
        print(f"✗ 予期しないエラー: {e}")
        return False

def test_gui_initialization():
    """GUI初期化テスト（表示はしない）"""
    try:
        print("GUI初期化テスト...")
        import tkinter as tk
        from gui.integrated_test_gui import IntegratedTestGUI
        
        # 非表示でrootウィンドウを作成
        root = tk.Tk()
        root.withdraw()  # ウィンドウを非表示にする
        
        # GUIアプリケーション初期化
        app = IntegratedTestGUI(root)
        print("✓ GUI初期化成功")
        
        # クリーンアップ
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ GUI初期化エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_setup():
    """環境セットアップテスト"""
    try:
        print("環境設定確認...")
        
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

def main():
    """メインテスト実行"""
    print("TechZip Pre-flight Checker - GUI動作確認テスト")
    print("=" * 60)
    
    tests = [
        ("モジュールインポート", test_gui_import),
        ("環境設定確認", test_environment_setup), 
        ("GUI初期化", test_gui_initialization),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 成功")
        else:
            print(f"❌ {test_name} 失敗")
    
    print("\n" + "=" * 60)
    print(f"テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！")
        print("GUIアプリケーションの準備ができています。")
        print("\n実行方法:")
        print("  python main_gui.py")
        print("  または")
        print("  run_gui.bat")
        return 0
    else:
        print("⚠️ 一部のテストが失敗しました。")
        print("依存関係を確認してください:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)