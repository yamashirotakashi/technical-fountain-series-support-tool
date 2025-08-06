"""TechZip Pre-flight Checker - GUI版メインエントリポイント
統合テストGUIアプリケーションの起動スクリプト
"""
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """GUI版アプリケーション起動"""
    try:
        # 環境設定の確認
        env_file = project_root / ".env"
        if not env_file.exists():
            print("警告: .envファイルが見つかりません")
            print("Gmail設定を確認してください")
        
        # GUI起動
        from gui.integrated_test_gui import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"必要なモジュールが見つかりません: {e}")
        print("依存関係をインストールしてください: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"アプリケーション起動エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()