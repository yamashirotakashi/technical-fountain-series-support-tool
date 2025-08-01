"""
技術の泉シリーズプロジェクト初期化ツール - EXE版メインエントリーポイント v1.1.0
Windows環境での単体実行用（デバッグ強化版）

バージョン管理:
- v1.0.0: 初回リリース
- v1.1.0: デバッグ強化、エラーハンドリング改善
"""

__version__ = "1.1.0"

import sys
import os
import traceback
import time
from pathlib import Path

# デバッグ用の詳細出力関数
def debug_print(message, error=False):
    """デバッグ情報の出力"""
    prefix = "ERROR" if error else "DEBUG"
    print(f"[{prefix}] {message}")
    sys.stdout.flush()  # 即座に出力

def keep_console_open():
    """コンソールを開いたままにする"""
    try:
        debug_print("コンソールを開いたままにします...")
        debug_print("何かキーを押してください...")
        input()
    except:
        debug_print("5秒待機してから終了します...")
        time.sleep(5)

def setup_exe_environment():
    """EXE実行環境のセットアップ"""
    try:
        debug_print("EXE環境のセットアップを開始...")
        
        # PyInstallerで実行されている場合の処理
        if getattr(sys, 'frozen', False):
            # EXE実行時のパス設定
            exe_dir = Path(sys.executable).parent
            app_path = exe_dir
            
            debug_print(f"EXE実行モード検出: {exe_dir}")
            
            # 必要なパスを環境変数に設定
            os.environ['TECHBRIDGE_EXE_MODE'] = '1'
            os.environ['TECHBRIDGE_EXE_DIR'] = str(exe_dir)
            
            # 設定ファイルのパス
            config_dir = exe_dir / "config"
            if config_dir.exists():
                os.environ['TECHBRIDGE_CONFIG_DIR'] = str(config_dir)
                debug_print(f"設定ディレクトリ設定: {config_dir}")
            else:
                debug_print("設定ディレクトリが見つかりません", error=True)
            
            debug_print(f"✅ EXE実行環境を検出: {exe_dir}")
        else:
            # 開発環境での実行
            app_path = Path(__file__).parent
            debug_print(f"✅ 開発環境で実行: {app_path}")
        
        # アプリケーションパスをPythonパスに追加
        if str(app_path) not in sys.path:
            sys.path.insert(0, str(app_path))
            debug_print(f"Pythonパスに追加: {app_path}")
        
        return True
        
    except Exception as e:
        debug_print(f"EXE環境セットアップ失敗: {e}", error=True)
        traceback.print_exc()
        return False

def check_dependencies():
    """依存関係の確認"""
    debug_print("依存関係の確認を開始...")
    
    required_modules = [
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'dotenv',
        'aiohttp',
        'slack_sdk',
        'google.auth',
        'googleapiclient'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            debug_print(f"✅ {module}")
        except ImportError as e:
            debug_print(f"✗ {module}: {e}", error=True)
            missing_modules.append(module)
    
    if missing_modules:
        debug_print(f"不足しているモジュール: {missing_modules}", error=True)
        return False
    
    debug_print("✅ 全ての依存関係が利用可能です")
    return True

def load_environment():
    """環境変数の読み込み"""
    debug_print("環境変数の読み込みを開始...")
    
    try:
        from dotenv import load_dotenv
        
        # EXE実行時の.envファイル検索
        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).parent
            env_candidates = [
                exe_dir / ".env",
                exe_dir / "config" / ".env",
                Path.cwd() / ".env"
            ]
        else:
            env_candidates = [
                Path(__file__).parent / ".env",
                Path(__file__).parent.parent.parent / ".env"
            ]
        
        debug_print(f"環境変数ファイル候補: {[str(p) for p in env_candidates]}")
        
        env_loaded = False
        for env_file in env_candidates:
            debug_print(f"チェック中: {env_file}")
            if env_file.exists():
                load_dotenv(env_file)
                debug_print(f"✅ 環境変数ファイルを読み込み: {env_file}")
                env_loaded = True
                break
        
        if not env_loaded:
            debug_print("⚠️ .envファイルが見つかりません。手動で環境変数を設定してください。")
        
        return True
        
    except Exception as e:
        debug_print(f"環境変数読み込みエラー: {e}", error=True)
        traceback.print_exc()
        return False

def initialize_qt():
    """Qt6の初期化"""
    debug_print("PyQt6の初期化を開始...")
    
    try:
        # Qt6のインポート（必要最小限）
        debug_print("PyQt6.QtCoreをインポート中...")
        from PyQt6.QtCore import QCoreApplication, qInstallMessageHandler
        
        debug_print("PyQt6.QtWidgetsをインポート中...")
        from PyQt6.QtWidgets import QApplication
        
        debug_print("PyQt6.QtGuiをインポート中...")
        from PyQt6.QtGui import QGuiApplication
        
        # Qt6のメッセージハンドラーを設定（デバッグ用）
        def qt_message_handler(mode, context, message):
            debug_print(f"Qt Message: {message}")
        
        qInstallMessageHandler(qt_message_handler)
        
        debug_print("✅ PyQt6の初期化完了")
        return True
        
    except Exception as e:
        debug_print(f"PyQt6初期化エラー: {e}", error=True)
        traceback.print_exc()
        return False

def main():
    """メインエントリーポイント（デバッグ強化版）"""
    print("=" * 60)
    print("技術の泉シリーズプロジェクト初期化ツール")
    print(f"デバッグ版 v{__version__}")
    print("=" * 60)
    print()
    
    try:
        # ステップ1: EXE環境のセットアップ
        debug_print("ステップ1: EXE環境のセットアップ")
        if not setup_exe_environment():
            debug_print("EXE環境のセットアップに失敗しました", error=True)
            keep_console_open()
            sys.exit(1)
        
        # ステップ2: 依存関係の確認
        debug_print("ステップ2: 依存関係の確認")
        if not check_dependencies():
            debug_print("依存関係の確認に失敗しました", error=True)
            keep_console_open()
            sys.exit(1)
        
        # ステップ3: 環境変数の読み込み
        debug_print("ステップ3: 環境変数の読み込み")
        if not load_environment():
            debug_print("環境変数の読み込みに失敗しました", error=True)
            keep_console_open()
            sys.exit(1)
        
        # ステップ4: PyQt6の初期化
        debug_print("ステップ4: PyQt6の初期化")
        if not initialize_qt():
            debug_print("PyQt6の初期化に失敗しました", error=True)
            keep_console_open()
            sys.exit(1)
        
        print()
        print(f"技術の泉シリーズプロジェクト初期化ツール v{__version__}")
        print("アプリケーションを起動中...")
        print("※ Qt6 GUIアプリケーションが起動します")
        print()
        
        # ステップ5: メインアプリケーションのインポートと実行
        debug_print("ステップ5: メインアプリケーションの起動")
        try:
            debug_print("main_windowモジュールをインポート中...")
            from main_window import main as main_app
            debug_print("✅ main_windowモジュールのインポート完了")
            
            debug_print("GUIアプリケーションを起動中...")
            main_app()
            debug_print("✅ アプリケーション正常終了")
            
        except ImportError as e:
            debug_print(f"main_windowモジュールのインポートエラー: {e}", error=True)
            debug_print("利用可能なPythonファイルを確認しています...")
            current_dir = Path(__file__).parent if not getattr(sys, 'frozen', False) else Path(sys.executable).parent
            py_files = list(current_dir.glob("*.py"))
            debug_print(f"利用可能なPythonファイル: {[f.name for f in py_files]}")
            raise
        
    except KeyboardInterrupt:
        debug_print("ユーザーによる中断")
        sys.exit(0)
    except ImportError as e:
        debug_print(f"✗ 必要なライブラリが見つかりません: {e}", error=True)
        debug_print("必要な依存関係がインストールされていることを確認してください。")
        traceback.print_exc()
        keep_console_open()
        sys.exit(1)
    except Exception as e:
        debug_print(f"✗ アプリケーション起動エラー: {e}", error=True)
        debug_print("詳細なエラー情報:")
        traceback.print_exc()
        keep_console_open()
        sys.exit(1)

if __name__ == "__main__":
    main()