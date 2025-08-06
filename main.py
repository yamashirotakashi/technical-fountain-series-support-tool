#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""技術の泉シリーズ制作支援ツール - エントリーポイント"""
import sys
import os
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加（インポート前に必要）
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# パス解決と環境変数管理システムをインポート
from utils.path_resolver import PathResolver
from utils.env_manager import EnvManager
from utils.config import reset_config

# 環境変数管理システムを初期化（.envファイルの読み込みを含む）
EnvManager.initialize()

# EXE環境では設定をリセットして最新の値を読み込む
if PathResolver.is_exe_environment():
    reset_config()

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow
from utils.logger import get_logger
from utils.startup_logger import StartupLogger


def main():
    """アプリケーションのエントリーポイント"""
    # ロガーを初期化
    logger = get_logger(__name__)
    
    # Phase 3-2: DI Container初期化
    logger.info("DI Container設定を初期化します")
    try:
        from core.di_container import configure_services
        configure_services()
        logger.info("DI Container設定完了")
    except Exception as e:
        logger.error(f"DI Container初期化エラー: {e}", exc_info=True)
        # DI設定が失敗してもアプリケーションを続行
    
    # 起動時ログ収集を開始
    startup_logger = StartupLogger()
    startup_logger.collect_startup_info()
    
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
    
    # 起動時ログをGUIに表示
    startup_logs = startup_logger.format_logs_for_display()
    window.log_panel.append_log("=== 起動時診断情報 ===")
    for line in startup_logs.split('\n'):
        window.log_panel.append_log(line)
    window.log_panel.append_log("=== 起動完了 ===")
    
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