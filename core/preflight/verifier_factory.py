"""Pre-flight Verifierのファクトリー"""
from typing import Optional
import os

from .verifier_base import PreflightVerifier
from .word2xhtml_scraper import Word2XhtmlScrapingVerifier
from .api_verifier import Word2XhtmlApiVerifier
from utils.logger import get_logger


class VerifierFactory:
    """検証実装のファクトリークラス
    
    環境変数や設定に基づいて適切なVerifierを生成します。
    """
    
    @staticmethod
    def create_verifier(mode: Optional[str] = None) -> PreflightVerifier:
        """Verifierを作成
        
        Args:
            mode: 動作モード ('api', 'scraping', None)
                 Noneの場合は環境変数から判定
                 
        Returns:
            適切なVerifierインスタンス
        """
        logger = get_logger(__name__)
        
        # モードの決定
        if mode is None:
            mode = os.getenv('PREFLIGHT_MODE', 'scraping').lower()
            
        logger.info(f"Pre-flight Verifierモード: {mode}")
        
        if mode == 'api':
            # API実装を使用
            api_key = os.getenv('WORD2XHTML_API_KEY')
            if not api_key:
                logger.warning("APIキーが設定されていません。スクレイピングモードにフォールバック")
                return Word2XhtmlScrapingVerifier()
                
            logger.info("APIモードで動作します")
            return Word2XhtmlApiVerifier(api_key)
            
        else:
            # デフォルト: スクレイピング実装を使用
            logger.info("スクレイピングモードで動作します")
            return Word2XhtmlScrapingVerifier()
            
    @staticmethod
    def is_api_available() -> bool:
        """APIが利用可能かチェック
        
        Returns:
            APIが利用可能な場合True
        """
        # 現在はAPIが提供されていないため常にFalse
        # 将来的にはAPIの疎通確認を実装
        return False