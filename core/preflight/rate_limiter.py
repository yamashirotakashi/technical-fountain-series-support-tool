"""レート制限管理モジュール"""
from __future__ import annotations

import time
from typing import Optional
from utils.logger import get_logger

# ConfigManagerをインポート
try:
    from src.slack_pdf_poster import ConfigManager
except ImportError:
    ConfigManager = None


class RateLimiter:
    """APIレート制限を管理するクラス"""
    
    def __init__(self, min_interval: Optional[float] = None, config_manager: Optional['ConfigManager'] = None):
        """
        Args:
            min_interval: リクエスト間の最小間隔（秒）
            config_manager: 設定管理インスタンス
        """
        self.logger = get_logger(__name__)
        self.config_manager = config_manager or (ConfigManager() if ConfigManager else None)
        
        # ConfigManagerから間隔設定を取得（デフォルト値付き）
        if min_interval is None:
            self.min_interval = self.config_manager.get("rate_limiter.min_interval", 5.0) if self.config_manager else 5.0
        else:
            self.min_interval = min_interval
            
        self.last_request_time: Optional[float] = None
        self.logger.info(f"レート制限間隔: {self.min_interval}秒")
        
    def wait_if_needed(self):
        """必要に応じて待機"""
        if self.last_request_time is None:
            self.last_request_time = time.time()
            return
            
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            self.logger.info(f"レート制限: {wait_time:.1f}秒待機します")
            time.sleep(wait_time)
            
        self.last_request_time = time.time()
        
    def reset(self):
        """タイマーをリセット"""
        self.last_request_time = None