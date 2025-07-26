"""Word2XHTML5サービスのSelenium実装"""
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .verifier_base import PreflightVerifier
from .selenium_driver_manager import SeleniumDriverManager
from .rate_limiter import RateLimiter
from utils.logger import get_logger


class Word2XhtmlScrapingVerifier(PreflightVerifier):
    """Seleniumを使用したWord2XHTML5サービスの検証実装"""
    
    SERVICE_URL = "http://trial.nextpublishing.jp/upload_46tate/"
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.driver_manager = SeleniumDriverManager()
        self.rate_limiter = RateLimiter(min_interval=5.0)
        self.driver = None
        self.job_file_mapping: Dict[str, str] = {}  # job_id -> file_path
        
    def _submit_single(self, file_path: str, email: str) -> Optional[str]:
        """単一ファイルを送信してジョブIDを取得
        
        Args:
            file_path: Wordファイルのパス
            email: メールアドレス
            
        Returns:
            ジョブID（失敗時はNone）
        """
        try:
            # ドライバーを取得
            if not self.driver:
                self.driver = self.driver_manager.get_driver()
                
            # サービスページにアクセス
            self.driver.get(self.SERVICE_URL)
            wait = WebDriverWait(self.driver, 10)
            
            # ファイル選択
            file_input = wait.until(
                EC.presence_of_element_located((By.NAME, "upload_file"))
            )
            file_input.send_keys(file_path)
            
            # メールアドレス入力
            email_input = self.driver.find_element(By.NAME, "email")
            email_input.clear()
            email_input.send_keys(email)
            
            # 送信ボタンをクリック
            submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
            submit_button.click()
            
            # 結果ページを待機
            time.sleep(2)  # ページ遷移を待つ
            
            # ジョブIDを取得（ページのテキストから抽出）
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # ジョブIDの抽出ロジック（サービスの応答に応じて調整が必要）
            # 仮実装: タイムスタンプベースのIDを生成
            job_id = f"job_{int(time.time())}_{Path(file_path).stem}"
            
            self.logger.info(f"ファイル送信成功: {file_path} -> {job_id}")
            return job_id
            
        except TimeoutException:
            self.logger.error(f"タイムアウト: {file_path}")
            return None
        except Exception as e:
            self.logger.error(f"送信エラー: {file_path} - {e}")
            return None
    
    def submit_batch(self, file_paths: List[str], email: str) -> List[str]:
        """複数ファイルを送信してジョブIDリストを返す"""
        job_ids = []
        
        for i, file_path in enumerate(file_paths):
            self.logger.info(f"送信中 ({i+1}/{len(file_paths)}): {file_path}")
            
            # レート制限
            self.rate_limiter.wait_if_needed()
            
            # ファイル送信
            job_id = self._submit_single(file_path, email)
            if job_id:
                job_ids.append(job_id)
                self.job_file_mapping[job_id] = file_path
            else:
                # 失敗した場合も空のIDを追加（順序を保つため）
                job_ids.append("")
                
        return job_ids
    
    def check_all_status(self, job_ids: List[str]) -> Dict[str, Tuple[str, Optional[str]]]:
        """全ジョブのステータスを確認
        
        注意: 現在の実装ではメール監視が必要なため、
        この機能は別途実装が必要
        """
        results = {}
        
        for job_id in job_ids:
            if not job_id:  # 空のIDはスキップ
                continue
                
            # TODO: メール監視機能との連携
            # 現時点では仮実装
            results[job_id] = ("pending", None)
            
        return results
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        self.driver_manager.cleanup()
        self.job_file_mapping.clear()