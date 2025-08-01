"""
技術の泉シリーズプロジェクト初期化ツール - EXE版メインエントリーポイント v1.1
Windows環境での単体実行用

バージョン管理:
- v1.0: 初回リリース（本番版）
- 改版時: 0.1ずつ増加 (例: 1.0 → 1.1 → 1.2 → 2.0)
"""

__version__ = "1.2"

import sys
import os
from pathlib import Path

# Windows EXE環境でのUnicode出力問題を解決
def safe_print(text: str):
    """Unicode文字を安全に出力"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Unicode文字を安全な文字に置き換え
        safe_text = text.replace("✅", "[OK]").replace("✗", "[ERROR]").replace("⚠️", "[WARN]")
        print(safe_text.encode('ascii', 'ignore').decode('ascii'))

def setup_exe_environment():
    """EXE実行環境のセットアップ"""
    # PyInstallerで実行されている場合の処理
    if getattr(sys, 'frozen', False):
        # EXE実行時のパス設定
        exe_dir = Path(sys.executable).parent
        app_path = exe_dir
        
        # 必要なパスを環境変数に設定
        os.environ['TECHBRIDGE_EXE_MODE'] = '1'
        os.environ['TECHBRIDGE_EXE_DIR'] = str(exe_dir)
        
        # 設定ファイルのパス
        config_dir = exe_dir / "config"
        if config_dir.exists():
            os.environ['TECHBRIDGE_CONFIG_DIR'] = str(config_dir)
        
        safe_print(f"✅ EXE実行環境を検出: {exe_dir}")
    else:
        # 開発環境での実行
        app_path = Path(__file__).parent
        safe_print(f"✅ 開発環境で実行: {app_path}")
    
    # アプリケーションパスをPythonパスに追加
    if str(app_path) not in sys.path:
        sys.path.insert(0, str(app_path))

def main():
    """メインエントリーポイント"""
    print("=" * 50)
    print("技術の泉シリーズプロジェクト初期化ツール")
    print("=" * 50)
    print()
    
    try:
        # EXE環境のセットアップ
        setup_exe_environment()
        
        # 環境変数の読み込み（EXE用）
        from pathlib import Path
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
        
        env_loaded = False
        for env_file in env_candidates:
            if env_file.exists():
                load_dotenv(env_file)
                safe_print(f"✅ 環境変数ファイルを読み込み: {env_file}")
                env_loaded = True
                break
        
        if not env_loaded:
            safe_print("⚠️ .envファイルが見つかりません。手動で環境変数を設定してください。")
        
        print()
        print(f"技術の泉シリーズプロジェクト初期化ツール v{__version__}")
        print("アプリケーションを起動中...")
        print("※ Qt6 GUIアプリケーションが起動します")
        print()
        
        # メインアプリケーションのインポートと実行
        from main_window import main
        main()
        
    except ImportError as e:
        safe_print(f"✗ 必要なライブラリが見つかりません: {e}")
        print("必要な依存関係がインストールされていることを確認してください。")
        sys.exit(1)
    except Exception as e:
        safe_print(f"✗ アプリケーション起動エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()