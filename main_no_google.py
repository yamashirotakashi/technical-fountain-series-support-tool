"""メインアプリケーション - Google Sheets機能無効版"""
import sys
import os
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 環境変数を読み込み
from dotenv import load_dotenv
load_dotenv()

# PyQt5の設定
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from gui.main_window_no_google import MainWindowNoGoogle
from utils.logger import get_logger


def main():
    """アプリケーションのメインエントリーポイント"""
    logger = get_logger(__name__)
    
    try:
        # Qt Applicationを作成
        app = QApplication(sys.argv)
        app.setApplicationName("技術の泉シリーズ制作支援ツール")
        app.setApplicationVersion("1.0.0")
        
        # DPIスケーリングを有効化
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # メインウィンドウを作成
        window = MainWindowNoGoogle()
        window.show()
        
        logger.info("アプリケーションを起動しました")
        
        # イベントループを開始
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"アプリケーション起動エラー: {e}", exc_info=True)
        
        # エラーダイアログを表示
        if 'app' in locals():
            QMessageBox.critical(
                None,
                "起動エラー",
                f"アプリケーションの起動に失敗しました:\n{str(e)}"
            )
        sys.exit(1)


if __name__ == "__main__":
    main()