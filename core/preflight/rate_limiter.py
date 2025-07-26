"""レート制限管理モジュール"""
import time
from typing import Optional
from utils.logger import get_logger


class RateLimiter:
    """APIレート制限を管理するクラス"""
    
    def __init__(self, min_interval: float = 5.0):
        """
        Args:
            min_interval: リクエスト間の最小間隔（秒）
        """
        self.min_interval = min_interval
        self.last_request_time: Optional[float] = None
        self.logger = get_logger(__name__)
        
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