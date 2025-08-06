#!/usr/bin/env python3
"""
NextPublishing アップロード検証専用スクレイピングアプリ
アップロードとその後のリダイレクト先の確認までを解析し、成功するまで実装する
"""
import sys
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import logging
from typing import Optional, Tuple, Dict, Any

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """詳細なログ設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('nextpublishing_verification.log', encoding='utf-8')
        ]
    )

class NextPublishingVerificationScraper:
    """NextPublishing アップロード検証スクレイピングクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.base_url = "http://trial.nextpublishing.jp/rapture/"
        self.username = "ep_user"  # 実際の認証情報は設定から取得
        self.password = None  # 設定から取得
        
        # 設定を読み込み
        self._load_config()
    
    def _load_config(self):
        """設定を読み込み"""
        try:
            from utils.config import get_config
            config = get_config()
            # NextPublishing認証情報を取得
            web_config = config.get_web_config()
            self.username = web_config.get('username', 'ep_user')
            self.password = web_config.get('password', '')
            
            if not self.password:
                # 環境変数からも試す
                import os
                self.password = os.environ.get('NEXTPUBLISHING_PASSWORD', '')
            
            self.logger.info(f"設定読み込み完了 - username: {self.username}")
        except Exception as e:
            self.logger.error(f"設定読み込みエラー: {e}")
            # デフォルト値（テスト用）
            self.password = "test_password"
    
    def setup_driver(self):
        """Selenium WebDriverを初期化"""
        self.logger.info("Chrome WebDriverを初期化中...")
        
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--headless=new')  # 新しいヘッドレスモード
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Basic認証の自動処理のため
        chrome_options.add_argument(f'--auth-server-whitelist=*nextpublishing.jp')
        chrome_options.add_argument(f'--auth-negotiate-delegate-whitelist=*nextpublishing.jp')
        
        try:
            # webdriver-managerでChromeDriverを自動管理
            import os
            os.environ['WDM_LOG'] = 'false'  # webdriver-managerの出力を抑制
            driver_path = ChromeDriverManager().install()
            self.logger.info(f"ChromeDriver path: {driver_path}")
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            self.logger.info("Chrome WebDriver初期化完了")
            return True
        except Exception as e:
            self.logger.error(f"WebDriver初期化エラー: {e}")
            return False
    
    def navigate_with_auth(self, url: str) -> bool:
        """Basic認証付きでURLにアクセス"""
        try:
            # Basic認証を含むURLを構成
            from urllib.parse import quote
            encoded_password = quote(self.password)
            auth_url = url.replace("http://", f"http://{self.username}:{encoded_password}@")
            self.logger.info(f"認証付きアクセス: {url}")
            
            self.driver.get(auth_url)
            
            # ページロードを待機
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.logger.info(f"ページタイトル: {self.driver.title}")
            self.logger.info(f"現在のURL: {self.driver.current_url}")
            
            return True
        except Exception as e:
            self.logger.error(f"認証付きナビゲーションエラー: {e}")
            return False
    
    def analyze_upload_form(self) -> Dict[str, Any]:
        """アップロードフォームを解析"""
        try:
            self.logger.info("=== フォーム解析開始 ===")
            
            # フォーム要素を探索
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            self.logger.info(f"検出されたフォーム数: {len(forms)}")
            
            form_info = {}
            
            for i, form in enumerate(forms):
                action = form.get_attribute("action")
                method = form.get_attribute("method")
                enctype = form.get_attribute("enctype")
                
                self.logger.info(f"フォーム{i+1}: action={action}, method={method}, enctype={enctype}")
                
                # ファイル入力要素を探索
                file_inputs = form.find_elements(By.CSS_SELECTOR, "input[type='file']")
                for j, file_input in enumerate(file_inputs):
                    name = file_input.get_attribute("name")
                    accept = file_input.get_attribute("accept")
                    self.logger.info(f"  ファイル入力{j+1}: name={name}, accept={accept}")
                    
                    if "userfile" in name or not name:
                        form_info = {
                            "form": form,
                            "action": action or self.driver.current_url,
                            "method": method or "POST",
                            "enctype": enctype or "multipart/form-data",
                            "file_input": file_input,
                            "file_input_name": name or "userfile"
                        }
                        break
            
            if not form_info:
                self.logger.warning("適切なアップロードフォームが見つかりません")
                # HTMLソースをログに出力（デバッグ用）
                html_source = self.driver.page_source[:1000]
                self.logger.debug(f"ページHTML（最初の1000文字）: {html_source}")
            
            return form_info
        except Exception as e:
            self.logger.error(f"フォーム解析エラー: {e}")
            return {}
    
    def perform_upload(self, file_path: Path, form_info: Dict[str, Any]) -> bool:
        """実際のファイルアップロードを実行"""
        try:
            self.logger.info("=== アップロード実行開始 ===")
            self.logger.info(f"アップロードファイル: {file_path}")
            self.logger.info(f"ファイルサイズ: {file_path.stat().st_size} bytes")
            
            # ファイル入力要素にファイルパスを設定
            file_input = form_info["file_input"]
            file_input.send_keys(str(file_path.absolute()))
            
            self.logger.info("ファイル選択完了")
            
            # その他の必要なフィールドを探して設定
            form = form_info["form"]
            
            # メールアドレスフィールドを探す
            email_inputs = form.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
            for email_input in email_inputs:
                name = email_input.get_attribute("name")
                if "mail" in name.lower() or "email" in name.lower():
                    email_input.clear()
                    email_input.send_keys("yamashiro.takashi@gmail.com")
                    self.logger.info(f"メールアドレス設定: {name}")
                    break
            
            # 送信前の状態を記録
            current_url = self.driver.current_url
            self.logger.info(f"送信前URL: {current_url}")
            
            # 送信ボタンを探して実行
            submit_buttons = form.find_elements(By.CSS_SELECTOR, "input[type='submit'], button[type='submit'], button")
            
            for button in submit_buttons:
                button_text = button.get_attribute("value") or button.text
                self.logger.info(f"送信ボタン候補: {button_text}")
                
                if "アップロード" in button_text or "送信" in button_text or "submit" in button_text.lower():
                    self.logger.info(f"送信ボタンをクリック: {button_text}")
                    button.click()
                    break
            else:
                # デフォルトで最初の送信ボタンをクリック
                if submit_buttons:
                    self.logger.info("デフォルト送信ボタンをクリック")
                    submit_buttons[0].click()
                else:
                    self.logger.error("送信ボタンが見つかりません")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"アップロード実行エラー: {e}")
            return False
    
    def monitor_redirect_and_success(self, timeout: int = 30) -> Tuple[bool, str, Optional[str]]:
        """リダイレクトと成功ページを監視"""
        try:
            self.logger.info("=== リダイレクト・成功監視開始 ===")
            
            start_time = time.time()
            initial_url = self.driver.current_url
            
            while time.time() - start_time < timeout:
                current_url = self.driver.current_url
                page_title = self.driver.title
                page_source = self.driver.page_source
                
                self.logger.info(f"監視中 - URL: {current_url}")
                self.logger.info(f"監視中 - タイトル: {page_title}")
                
                # 成功パターンを検出
                success_patterns = [
                    "アップロード完了",
                    "受付完了",
                    "success",
                    "成功",
                    "受付番号",
                    "管理番号",
                    "ID:",
                    "番号："
                ]
                
                page_text = page_source.lower()
                for pattern in success_patterns:
                    if pattern.lower() in page_text:
                        self.logger.info(f"✅ 成功パターン検出: {pattern}")
                        
                        # 管理番号を抽出を試みる（同じURLでも内容が変わっていることを確認）
                        import re
                        control_number_patterns = [
                            r'受付番号[:：]\s*([A-Z0-9\-]+)',
                            r'管理番号[:：]\s*([A-Z0-9\-]+)',
                            r'ID[:：]\s*([A-Z0-9\-]+)',
                            r'番号[:：]\s*([A-Z0-9\-]+)',
                            r'整理番号[:：]\s*([A-Z0-9\-]+)'
                        ]
                        
                        control_number = None
                        for cn_pattern in control_number_patterns:
                            match = re.search(cn_pattern, page_source)
                            if match:
                                control_number = match.group(1)
                                self.logger.info(f"📋 管理番号抽出: {control_number}")
                                break
                        
                        return True, f"アップロード成功 - URL: {current_url}", control_number
                
                # エラーパターンを検出
                error_patterns = [
                    "error",
                    "エラー",
                    "失敗",
                    "failed",
                    "invalid",
                    "不正",
                    "ファイルサイズ",
                    "形式が不正"
                ]
                
                for pattern in error_patterns:
                    if pattern.lower() in page_text:
                        self.logger.error(f"❌ エラーパターン検出: {pattern}")
                        return False, f"アップロードエラー - パターン: {pattern} - URL: {current_url}", None
                
                # URLの変化を検出
                if current_url != initial_url:
                    self.logger.info(f"🔄 リダイレクト検出: {initial_url} -> {current_url}")
                    initial_url = current_url
                
                time.sleep(1)  # 1秒待機
            
            # タイムアウト
            self.logger.warning(f"⏰ 監視タイムアウト（{timeout}秒）")
            final_url = self.driver.current_url
            return False, f"監視タイムアウト - 最終URL: {final_url}", None
            
        except Exception as e:
            self.logger.error(f"リダイレクト・成功監視エラー: {e}")
            return False, f"監視エラー: {e}", None
    
    def capture_debug_info(self):
        """デバッグ情報をキャプチャ"""
        try:
            # スクリーンショット保存
            screenshot_path = Path("debug_screenshot.png")
            self.driver.save_screenshot(str(screenshot_path))
            self.logger.info(f"スクリーンショット保存: {screenshot_path}")
            
            # HTMLソース保存
            html_path = Path("debug_page_source.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            self.logger.info(f"HTMLソース保存: {html_path}")
            
        except Exception as e:
            self.logger.error(f"デバッグ情報キャプチャエラー: {e}")
    
    def verify_upload(self, file_path: Path) -> Tuple[bool, str, Optional[str]]:
        """完全なアップロード検証プロセスを実行"""
        try:
            self.logger.info("=== NextPublishing アップロード検証開始 ===")
            
            # WebDriverセットアップ
            if not self.setup_driver():
                return False, "WebDriver初期化失敗", None
            
            # Basic認証でサイトにアクセス
            if not self.navigate_with_auth(self.base_url):
                return False, "サイトアクセス失敗", None
            
            # フォーム解析
            form_info = self.analyze_upload_form()
            if not form_info:
                self.capture_debug_info()
                return False, "アップロードフォームが見つかりません", None
            
            # ファイルアップロード実行
            if not self.perform_upload(file_path, form_info):
                self.capture_debug_info()
                return False, "ファイルアップロード失敗", None
            
            # リダイレクトと成功監視
            success, message, control_number = self.monitor_redirect_and_success()
            
            if success:
                self.logger.info("✅ アップロード検証成功！")
            else:
                self.logger.error("❌ アップロード検証失敗")
                self.capture_debug_info()
            
            return success, message, control_number
            
        except Exception as e:
            self.logger.error(f"検証プロセスエラー: {e}")
            self.capture_debug_info()
            return False, f"検証プロセスエラー: {e}", None
        
        finally:
            # クリーンアップ
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriverクリーンアップ完了")
    
    def generate_feedback(self, success: bool, message: str, control_number: Optional[str]) -> Dict[str, Any]:
        """メインアプリケーションへのフィードバック情報を生成"""
        feedback = {
            "verification_success": success,
            "message": message,
            "control_number": control_number,
            "timestamp": time.time(),
            "recommendations": []
        }
        
        if success:
            feedback["recommendations"].extend([
                "Selenium WebDriverアプローチの採用を推奨",
                "Basic認証をWebDriverで自動処理",
                "フォーム要素の動的検出実装",
                "リダイレクト先での成功パターン検出実装",
                "管理番号の正規表現抽出実装"
            ])
        else:
            feedback["recommendations"].extend([
                "HTTP requestsアプローチは不適切",
                "Selenium WebDriverでのブラウザ自動化が必須",
                "セッション管理とCookieハンドリングが重要",
                "JavaScript実行環境が必要な可能性",
                "フォーム解析の改善が必要"
            ])
        
        return feedback

def main():
    """メイン実行関数"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("NextPublishing アップロード検証専用スクレイピングアプリ")
    print("=" * 60)
    
    # テストファイルを準備
    test_file = Path("venv/Lib/site-packages/docx/templates/default.docx")
    if not test_file.exists():
        logger.error(f"テストファイルが見つかりません: {test_file}")
        return False
    
    # 検証実行
    scraper = NextPublishingVerificationScraper()
    success, message, control_number = scraper.verify_upload(test_file)
    
    # フィードバック生成
    feedback = scraper.generate_feedback(success, message, control_number)
    
    # 結果出力
    print("\n=== 検証結果 ===")
    print(f"成功: {'✅' if success else '❌'}")
    print(f"メッセージ: {message}")
    if control_number:
        print(f"管理番号: {control_number}")
    
    print("\n=== メインアプリへのフィードバック ===")
    for recommendation in feedback["recommendations"]:
        print(f"- {recommendation}")
    
    # フィードバック情報をファイルに保存
    import json
    feedback_file = Path("nextpublishing_verification_feedback.json")
    with open(feedback_file, 'w', encoding='utf-8') as f:
        json.dump(feedback, f, ensure_ascii=False, indent=2)
    
    logger.info(f"フィードバック情報保存: {feedback_file}")
    
    print("=" * 60)
    print("SUCCESS: 検証完了" if success else "FAILED: 検証失敗")
    print("詳細ログ: nextpublishing_verification.log")
    print(f"フィードバック: {feedback_file}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)