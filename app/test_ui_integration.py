"""
UI統合テストスクリプト
Phase 0-3: 統合UIの動作確認
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.ui.main_window_integrated import main


if __name__ == "__main__":
    print("=== Phase 0-3: UI統合テスト ===")
    print("統合メインウィンドウを起動します...")
    
    try:
        main()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()