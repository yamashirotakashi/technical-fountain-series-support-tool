"""Seleniumドライバー管理モジュール"""
import os
import platform
import zipfile
import requests
from pathlib import Path
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from utils.logger import get_logger


class SeleniumDriverManager:
    """ChromeDriverの自動管理クラス"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.driver_dir = Path.home() / ".techzip" / "drivers"
        self.driver_dir.mkdir(parents=True, exist_ok=True)
        self.driver: Optional[webdriver.Chrome] = None
        
    def _get_chrome_version(self) -> str:
        """インストールされているChromeのバージョンを取得"""
        try:
            # Windows
            if platform.system() == "Windows":
                import winreg
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                       r"Software\Google\Chrome\BLBeacon")
                    version, _ = winreg.QueryValueEx(key, "version")
                    winreg.CloseKey(key)
                    return version
                except:
                    pass
                    
            # macOS/Linux - 簡易的にデフォルトバージョンを返す
            return "120.0.0.0"  # デフォルトバージョン
            
        except Exception as e:
            self.logger.warning(f"Chromeバージョン取得失敗: {e}")
            return "120.0.0.0"
    
    def _download_chromedriver(self, version: str) -> Path:
        """ChromeDriverをダウンロード"""
        system = platform.system().lower()
        if system == "windows":
            filename = "chromedriver-win64.zip"
            executable = "chromedriver.exe"
        elif system == "darwin":
            filename = "chromedriver-mac-x64.zip"
            executable = "chromedriver"
        else:
            filename = "chromedriver-linux64.zip"
            executable = "chromedriver"
            
        # ChromeDriver URLを構築
        major_version = version.split('.')[0]
        base_url = "https://storage.googleapis.com/chrome-for-testing-public"
        
        # バージョンに応じたURLを構築
        driver_url = f"{base_url}/{version}/{filename}"
        
        # ダウンロード先
        zip_path = self.driver_dir / filename
        driver_path = self.driver_dir / executable
        
        # 既にダウンロード済みならスキップ
        if driver_path.exists():
            return driver_path
            
        try:
            # ダウンロード
            self.logger.info(f"ChromeDriverをダウンロード中: {driver_url}")
            response = requests.get(driver_url, stream=True)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            # 解凍
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.driver_dir)
                
            # 実行権限を付与（Unix系）
            if platform.system() != "Windows":
                os.chmod(driver_path, 0o755)
                
            # ZIPファイルを削除
            zip_path.unlink()
            
            self.logger.info(f"ChromeDriverのダウンロード完了: {driver_path}")
            return driver_path
            
        except Exception as e:
            self.logger.error(f"ChromeDriverのダウンロード失敗: {e}")
            # フォールバック: システムのPATHから探す
            return "chromedriver"
    
    def get_driver(self) -> webdriver.Chrome:
        """WebDriverインスタンスを取得"""
        if self.driver:
            return self.driver
            
        try:
            # ChromeDriverのパスを取得
            chrome_version = self._get_chrome_version()
            driver_path = self._download_chromedriver(chrome_version)
            
            # Chrome オプション
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            # ヘッドレスモード（オプション）
            # options.add_argument('--headless')
            
            # ログを抑制
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            # ドライバーを作成
            service = Service(str(driver_path))
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # ウィンドウサイズを設定
            self.driver.set_window_size(1280, 800)
            
            self.logger.info("ChromeDriverの起動に成功")
            return self.driver
            
        except WebDriverException as e:
            self.logger.error(f"ChromeDriver起動エラー: {e}")
            raise
        except Exception as e:
            self.logger.error(f"予期しないエラー: {e}")
            raise
    
    def cleanup(self):
        """ドライバーをクリーンアップ"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("ChromeDriverを終了しました")
            except Exception as e:
                self.logger.warning(f"ChromeDriver終了時エラー: {e}")
            finally:
                self.driver = None