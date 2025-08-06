#!/usr/bin/env python3
"""
シンプルなSeleniumアップロードテスト
直接Basic認証とフォームアップロードを試みる
"""
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_simple_upload():
    """シンプルなアップロードテスト"""
    
    # 設定値
    username = "ep_user"
    password = "Nextpublishing20241218@2024"  # 実際のパスワード
    base_url = "http://trial.nextpublishing.jp/rapture/"
    test_file = Path("venv/Lib/site-packages/docx/templates/default.docx")
    
    if not test_file.exists():
        logger.error(f"テストファイルが見つかりません: {test_file}")
        return False
    
    logger.info("Chrome WebDriverを初期化中...")
    
    # Chrome Options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = None
    try:
        # WebDriver初期化
        import os
        os.environ['WDM_LOG'] = 'false'
        driver_path = ChromeDriverManager().install()
        logger.info(f"ChromeDriver: {driver_path}")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        
        logger.info("WebDriver初期化完了")
        
        # Basic認証付きでアクセス
        from urllib.parse import quote
        encoded_password = quote(password)
        auth_url = base_url.replace("http://", f"http://{username}:{encoded_password}@")
        
        logger.info(f"アクセス中: {base_url}")
        driver.get(auth_url)
        
        # ページロード待機
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        logger.info(f"ページタイトル: {driver.title}")
        logger.info(f"現在のURL: {driver.current_url}")
        
        # フォーム要素を探す
        forms = driver.find_elements(By.TAG_NAME, "form")
        logger.info(f"検出されたフォーム数: {len(forms)}")
        
        if forms:
            form = forms[0]
            
            # ファイル入力要素を探す
            file_inputs = form.find_elements(By.CSS_SELECTOR, "input[type='file']")
            logger.info(f"ファイル入力要素数: {len(file_inputs)}")
            
            if file_inputs:
                file_input = file_inputs[0]
                logger.info(f"ファイル入力name: {file_input.get_attribute('name')}")
                
                # ファイルを選択
                file_input.send_keys(str(test_file.absolute()))
                logger.info("ファイルを選択しました")
                
                # メールアドレスフィールドを探す
                text_inputs = form.find_elements(By.CSS_SELECTOR, "input[type='text']")
                for text_input in text_inputs:
                    name = text_input.get_attribute("name") or ""
                    if "mail" in name.lower():
                        text_input.clear()
                        text_input.send_keys("yamashiro.takashi@gmail.com")
                        logger.info(f"メールアドレスを設定: {name}")
                        break
                
                # 送信ボタンを探す
                submit_buttons = form.find_elements(By.CSS_SELECTOR, "input[type='submit'], button")
                logger.info(f"送信ボタン候補数: {len(submit_buttons)}")
                
                if submit_buttons:
                    button = submit_buttons[0]
                    button_text = button.get_attribute("value") or button.text
                    logger.info(f"送信ボタンをクリック: {button_text}")
                    
                    # 送信前のURL
                    before_url = driver.current_url
                    
                    # 送信
                    button.click()
                    
                    # 結果を待機（最大30秒）
                    logger.info("アップロード結果を待機中...")
                    start_time = time.time()
                    
                    while time.time() - start_time < 30:
                        current_url = driver.current_url
                        page_source = driver.page_source.lower()
                        
                        # URLが変わったか、ページ内容が変わったかチェック
                        if current_url != before_url:
                            logger.info(f"URLが変わりました: {before_url} -> {current_url}")
                        
                        # 成功パターンチェック
                        success_patterns = ["アップロード完了", "受付完了", "success", "管理番号", "受付番号"]
                        for pattern in success_patterns:
                            if pattern.lower() in page_source:
                                logger.info(f"✅ 成功パターン検出: {pattern}")
                                
                                # HTMLソース保存（デバッグ用）
                                with open("success_page.html", "w", encoding="utf-8") as f:
                                    f.write(driver.page_source)
                                logger.info("成功ページをsuccess_page.htmlに保存しました")
                                
                                return True
                        
                        # エラーパターンチェック
                        error_patterns = ["error", "エラー", "失敗", "invalid"]
                        for pattern in error_patterns:
                            if pattern.lower() in page_source and "error" not in before_url:
                                logger.error(f"❌ エラーパターン検出: {pattern}")
                                return False
                        
                        time.sleep(1)
                    
                    logger.warning("タイムアウト - 成功/エラーパターンが検出されませんでした")
                    
                    # 最終的なページソースを保存
                    with open("timeout_page.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    logger.info("タイムアウト時のページをtimeout_page.htmlに保存しました")
        
        # デバッグ用：現在のページソースを保存
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info("デバッグ用ページをdebug_page.htmlに保存しました")
        
        # スクリーンショット保存
        driver.save_screenshot("debug_screenshot.png")
        logger.info("スクリーンショットをdebug_screenshot.pngに保存しました")
        
        return False
        
    except Exception as e:
        logger.error(f"エラー発生: {e}")
        return False
    
    finally:
        if driver:
            driver.quit()
            logger.info("WebDriverをクリーンアップしました")

if __name__ == "__main__":
    print("=== シンプルなSeleniumアップロードテスト ===")
    success = test_simple_upload()
    print(f"\n結果: {'✅ 成功' if success else '❌ 失敗'}")