"""
TechDisposal Analyzer メインエントリーポイント - Qt6ベース
単一責任: アプリケーションの起動と初期化
"""
import sys
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.modules.techbook27_analyzer.ui.base_window import create_app
from app.modules.techbook27_analyzer.ui.analyzer_window import TechDisposalAnalyzerWindow
from app.modules.techbook27_analyzer.utils.logger import setup_logging


def main():
    """メインエントリーポイント"""
    # ロギングのセットアップ
    logger = setup_logging(
        app_name="TechDisposalAnalyzer",
        log_level="INFO",
        log_dir="logs"
    )
    
    logger.info("TechDisposal Analyzer (Qt6) を起動します")
    
    try:
        # Qt6アプリケーション作成
        app = create_app()
        
        # メインウィンドウ作成
        window = TechDisposalAnalyzerWindow()
        window.show_window()
        
        # アプリケーション実行
        sys.exit(app.exec())
        
    except Exception as e:
        logger.exception("アプリケーション実行中にエラーが発生しました")
        raise
    finally:
        logger.info("TechDisposal Analyzer を終了します")


if __name__ == "__main__":
    main()