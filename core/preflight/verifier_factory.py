"""Pre-flight Verifierのファクトリー"""
from typing import Optional
import os

from .verifier_base import PreflightVerifier
from .word2xhtml_scraper import Word2XhtmlScrapingVerifier
from .api_verifier import Word2XhtmlApiVerifier
from utils.logger import get_logger

# ConfigManagerをインポート
try:
    from src.slack_pdf_poster import ConfigManager
except ImportError:
    ConfigManager = None


class VerifierFactory:
    """検証実装のファクトリークラス
from __future__ import annotations
    
    環境変数や設定に基づいて適切なVerifierを生成します。
    """
    
    @staticmethod
    def create_verifier(mode: Optional[str] = None, config_manager: Optional['ConfigManager'] = None) -> PreflightVerifier:
        """Verifierを作成
        
        Args:
            mode: 動作モード ('api', 'scraping', None)
                 Noneの場合は環境変数から判定
            config_manager: 設定管理インスタンス
                 
        Returns:
            適切なVerifierインスタンス
        """
        logger = get_logger(__name__)
        
        # ConfigManagerインスタンスの作成
        if not config_manager and ConfigManager:
            config_manager = ConfigManager()
        
        # モードの決定
        if mode is None:
            if config_manager:
                mode = config_manager.get('verifier.default_mode', 'scraping').lower()
            else:
                mode = os.getenv('PREFLIGHT_MODE', 'scraping').lower()
                logger.warning("ConfigManagerが利用できません。環境変数からモードを取得します。")
            
        logger.info(f"Pre-flight Verifierモード: {mode}")
        
        if mode == 'api':
            # API実装を使用
            if config_manager:
                api_key = config_manager.get('api.word2xhtml.api_key')
            else:
                api_key = os.getenv('WORD2XHTML_API_KEY')
                
            if not api_key:
                logger.warning("APIキーが設定されていません。スクレイピングモードにフォールバック")
                return Word2XhtmlScrapingVerifier(config_manager)
                
            logger.info("APIモードで動作します")
            return Word2XhtmlApiVerifier(api_key, config_manager)
            
        else:
            # デフォルト: スクレイピング実装を使用
            logger.info("スクレイピングモードで動作します")
            return Word2XhtmlScrapingVerifier(config_manager)
            
    @staticmethod
    def is_api_available() -> bool:
        """APIが利用可能かチェック
        
        Returns:
            APIが利用可能な場合True
        """
        # 現在はAPIが提供されていないため常にFalse
        # 将来的にはAPIの疎通確認を実装
        return False