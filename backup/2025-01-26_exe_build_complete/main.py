#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""技術の泉シリーズ制作支援ツール - エントリーポイント"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow
from utils.logger import get_logger


def main():
    """アプリケーションのエントリーポイント"""
    # ロガーを初期化
    logger = get_logger(__name__)
    logger.info("アプリケーションを起動します")
    
    # High DPI対応（Qt6では自動的に有効）
    # Qt6ではこれらの属性は削除されているため、設定不要
    
    # アプリケーションを作成
    app = QApplication(sys.argv)
    app.setApplicationName("技術の泉シリーズ制作支援ツール")
    app.setOrganizationName("Technical Fountain")
    
    # スタイルを設定
    app.setStyle("Fusion")
    
    # メインウィンドウを作成して表示
    window = MainWindow()
    window.show()
    
    logger.info("メインウィンドウを表示しました")
    
    # アプリケーションを実行
    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"アプリケーションエラー: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()