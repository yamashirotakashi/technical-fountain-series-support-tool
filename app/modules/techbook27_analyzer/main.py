"""
TechBook27 Analyzer メインエントリーポイント
単一責任: アプリケーションの起動と初期化
"""
import sys
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.modules.techbook27_analyzer.ui.analyzer_window import TechBook27AnalyzerWindow
from app.modules.techbook27_analyzer.utils.logger import setup_logging


def main():
    """メインエントリーポイント"""
    # ロギングのセットアップ
    logger = setup_logging(
        app_name="TechBook27Analyzer",
        log_level="INFO",
        log_dir="logs"
    )
    
    logger.info("TechBook27 Analyzer を起動します")
    
    try:
        # アプリケーション起動
        app = TechBook27AnalyzerWindow()
        app.mainloop()
        
    except Exception as e:
        logger.exception("アプリケーション実行中にエラーが発生しました")
        raise
    finally:
        logger.info("TechBook27 Analyzer を終了します")


if __name__ == "__main__":
    main()