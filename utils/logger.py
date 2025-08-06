from __future__ import annotations
"""ログ管理モジュール"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class LoggerManager:
    """アプリケーション全体のログを管理するクラス"""
    
    def __init__(self, log_dir: str = "logs", app_name: str = "TechnicalFountainTool"):
        """
        ログマネージャーを初期化
        
        Args:
            log_dir: ログファイルを保存するディレクトリ
            app_name: アプリケーション名
        """
        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self.log_handlers = []
        
        # ログディレクトリを作成
        self.log_dir.mkdir(exist_ok=True)
        
        # ログファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"{app_name}_{timestamp}.log"
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        指定された名前のロガーを取得
        
        Args:
            name: ロガー名
        
        Returns:
            設定済みのロガー
        """
        logger = logging.getLogger(name)
        
        # すでに設定済みの場合はそのまま返す
        if logger.handlers:
            return logger
        
        logger.setLevel(logging.DEBUG)
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # ファイルハンドラー
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # ハンドラーを追加
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        self.log_handlers.extend([console_handler, file_handler])
        
        return logger
    
    def add_gui_handler(self, gui_handler: logging.Handler):
        """
        GUI用のログハンドラーを追加
        
        Args:
            gui_handler: GUIに表示するためのハンドラー
        """
        # すべての既存のロガーにGUIハンドラーを追加
        for name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(name)
            if name.startswith(self.app_name):
                logger.addHandler(gui_handler)
        
        self.log_handlers.append(gui_handler)
    
    def close(self):
        """すべてのハンドラーを閉じる"""
        for handler in self.log_handlers:
            handler.close()


# シングルトンインスタンス
_logger_manager = None


def get_logger_manager() -> LoggerManager:
    """ログマネージャーのシングルトンインスタンスを取得"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager


def get_logger(name: str) -> logging.Logger:
    """
    ロガーを取得するヘルパー関数
    
    Args:
        name: ロガー名
    
    Returns:
        設定済みのロガー
    """
    return get_logger_manager().get_logger(name)