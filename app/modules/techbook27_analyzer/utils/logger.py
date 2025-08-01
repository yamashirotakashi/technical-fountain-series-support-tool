"""
ロガーモジュール
単一責任: ログ出力の統一管理
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler


class LoggerManager:
    """ログ管理クラス"""
    
    def __init__(self, app_name: str = "TechDisposalAnalyzer", 
                 log_dir: Optional[str] = None):
        """
        Args:
            app_name: アプリケーション名
            log_dir: ログディレクトリ（Noneの場合はlogsディレクトリを作成）
        """
        self.app_name = app_name
        self.log_dir = self._setup_log_directory(log_dir)
        self.logger = None
        
    def _setup_log_directory(self, log_dir: Optional[str]) -> Path:
        """ログディレクトリのセットアップ"""
        if log_dir:
            path = Path(log_dir)
        else:
            path = Path("logs")
            
        path.mkdir(exist_ok=True)
        return path
        
    def setup_logger(self, log_level: str = "INFO") -> logging.Logger:
        """
        ロガーをセットアップ
        
        Args:
            log_level: ログレベル
            
        Returns:
            logging.Logger: 設定済みロガー
        """
        # ロガーを取得
        logger = logging.getLogger(self.app_name)
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # 既存のハンドラーをクリア
        logger.handlers.clear()
        
        # フォーマッター
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # ファイルハンドラー（ローテーション付き）
        log_file = self.log_dir / f"{self.app_name}_{datetime.now():%Y%m%d}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # エラー専用ファイルハンドラー
        error_file = self.log_dir / f"{self.app_name}_error_{datetime.now():%Y%m%d}.log"
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
        self.logger = logger
        return logger
        
    def get_logger(self, module_name: Optional[str] = None) -> logging.Logger:
        """
        モジュール用のロガーを取得
        
        Args:
            module_name: モジュール名
            
        Returns:
            logging.Logger: ロガー
        """
        if not self.logger:
            self.setup_logger()
            
        if module_name:
            return logging.getLogger(f"{self.app_name}.{module_name}")
        return self.logger
        
    def cleanup_old_logs(self, days: int = 30) -> None:
        """
        古いログファイルを削除
        
        Args:
            days: 保持日数
        """
        if not self.log_dir.exists():
            return
            
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for log_file in self.log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    if self.logger:
                        self.logger.info(f"古いログファイルを削除: {log_file.name}")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"ログファイル削除エラー: {log_file.name} - {str(e)}")


# グローバルインスタンス
_logger_manager = LoggerManager()


def setup_logging(app_name: str = "TechDisposalAnalyzer", 
                  log_level: str = "INFO",
                  log_dir: Optional[str] = None) -> logging.Logger:
    """
    ロギングをセットアップする便利関数
    
    Args:
        app_name: アプリケーション名
        log_level: ログレベル
        log_dir: ログディレクトリ
        
    Returns:
        logging.Logger: 設定済みロガー
    """
    global _logger_manager
    _logger_manager = LoggerManager(app_name, log_dir)
    return _logger_manager.setup_logger(log_level)


def get_logger(module_name: Optional[str] = None) -> logging.Logger:
    """
    ロガーを取得する便利関数
    
    Args:
        module_name: モジュール名
        
    Returns:
        logging.Logger: ロガー
    """
    return _logger_manager.get_logger(module_name)