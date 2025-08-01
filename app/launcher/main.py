"""
TECHGATEランチャー エントリーポイント
Phase 1: ランチャーのメイン実行ファイル
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.launcher.ui.launcher_window import main


if __name__ == "__main__":
    print("=== TECHGATE ランチャー ===")
    print("Phase 1: TECHGATEランチャー基本実装")
    print("起動中...")
    
    try:
        main()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        input("Enterキーを押して終了...")