"""Word2XHTML5サービスのSelenium実装"""
import time
import re
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
        
    def _extract_job_id(self, page_text: str) -> Optional[str]:
        """ページテキストからジョブIDを抽出
        
        Args:
            page_text: ページのテキスト内容
            
        Returns:
            抽出されたジョブID（見つからない場合はNone）
        """
        # 典型的なパターン:
        # 1. "受付番号: XXXXX" または "Job ID: XXXXX"
        # 2. "処理ID: XXXXX"
        # 3. メール内容に含まれるパターン
        
        patterns = [
            r'受付番号[:：]\s*(\S+)',
            r'Job\s*ID[:：]\s*(\S+)',
            r'処理ID[:：]\s*(\S+)',
            r'受付ID[:：]\s*(\S+)',
            r'整理番号[:：]\s*(\S+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1)
                
        # パターンマッチしない場合、タイムスタンプベースのIDを生成
        return None
        
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
            self.logger.info(f"アクセス中: {self.SERVICE_URL}")
            self.driver.get(self.SERVICE_URL)
            wait = WebDriverWait(self.driver, 20)
            
            # ページロード完了を待機
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
            
            # フォームの要素を探す（複数の可能性を考慮）
            file_input = None
            for selector in [
                (By.NAME, "upload_file"),
                (By.NAME, "file"),
                (By.NAME, "docx_file"),
                (By.XPATH, "//input[@type='file']"),
                (By.CSS_SELECTOR, "input[type='file']")
            ]:
                try:
                    file_input = self.driver.find_element(*selector)
                    break
                except NoSuchElementException:
                    continue
                    
            if not file_input:
                raise Exception("ファイル入力フィールドが見つかりません")
                
            # ファイルを選択
            self.logger.info(f"ファイル選択: {file_path}")
            file_input.send_keys(str(Path(file_path).absolute()))
            
            # メールアドレス入力フィールドを探す
            email_input = None
            for selector in [
                (By.NAME, "email"),
                (By.NAME, "mail"),
                (By.NAME, "email_address"),
                (By.XPATH, "//input[@type='email']"),
                (By.XPATH, "//input[contains(@placeholder, 'メール')]"),
                (By.XPATH, "//input[contains(@placeholder, 'mail')]")
            ]:
                try:
                    email_input = self.driver.find_element(*selector)
                    break
                except NoSuchElementException:
                    continue
                    
            if not email_input:
                raise Exception("メールアドレス入力フィールドが見つかりません")
                
            # メールアドレスを入力
            self.logger.info(f"メールアドレス入力: {email}")
            email_input.clear()
            email_input.send_keys(email)
            
            # 送信ボタンを探す
            submit_button = None
            for selector in [
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//input[@value='送信']"),
                (By.XPATH, "//button[contains(text(), '送信')]"),
                (By.XPATH, "//input[contains(@value, 'アップロード')]"),
                (By.XPATH, "//button[contains(text(), 'アップロード')]")
            ]:
                try:
                    submit_button = self.driver.find_element(*selector)
                    break
                except NoSuchElementException:
                    continue
                    
            if not submit_button:
                raise Exception("送信ボタンが見つかりません")
                
            # 送信前のページURLを記録
            current_url = self.driver.current_url
            
            # 送信ボタンをクリック
            self.logger.info("送信ボタンをクリック")
            submit_button.click()
            
            # ページ遷移またはアラートを待機
            time.sleep(3)
            
            # アラートの処理
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                self.logger.info(f"アラート: {alert_text}")
                alert.accept()
            except:
                pass
                
            # 結果ページの内容を取得
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            self.logger.debug(f"ページテキスト（最初の500文字）: {page_text[:500]}")
            
            # ジョブIDを抽出
            job_id = self._extract_job_id(page_text)
            
            # ジョブIDが見つからない場合、タイムスタンプベースのIDを生成
            if not job_id:
                job_id = f"job_{int(time.time() * 1000)}_{Path(file_path).stem}"
                self.logger.warning(f"ジョブIDが見つからないため生成: {job_id}")
            
            self.logger.info(f"ファイル送信成功: {file_path} -> {job_id}")
            return job_id
            
        except TimeoutException:
            self.logger.error(f"タイムアウト: {file_path}")
            return None
        except Exception as e:
            self.logger.error(f"送信エラー: {file_path} - {e}", exc_info=True)
            # スクリーンショットを保存（デバッグ用）
            if self.driver:
                try:
                    screenshot_path = Path.home() / ".techzip" / "debug" / f"error_{int(time.time())}.png"
                    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                    self.driver.save_screenshot(str(screenshot_path))
                    self.logger.info(f"エラー時のスクリーンショット: {screenshot_path}")
                except:
                    pass
            return None
    
    def submit_batch(self, file_paths: List[str], email: str) -> List[str]:
        """複数ファイルを送信してジョブIDリストを返す"""
        job_ids = []
        
        for i, file_path in enumerate(file_paths):
            self.logger.info(f"送信中 ({i+1}/{len(file_paths)}): {file_path}")
            
            # レート制限
            if i > 0:  # 最初のファイルは待機不要
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
        
        注意: この実装ではバッチプロセッサーがメール監視を直接行うため、
        このメソッドは使用されません。将来のAPI移行時に使用予定。
        """
        self.logger.info("check_all_statusは現在未使用です。バッチプロセッサーがメール監視を行います。")
        
        # 将来のAPI実装のためのプレースホルダー
        results = {}
        for job_id in job_ids:
            if job_id:
                results[job_id] = ("pending", None)
                
        return results
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        self.driver_manager.cleanup()
        self.job_file_mapping.clear()