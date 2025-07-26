"""Seleniumドライバー管理モジュール"""
import os
import platform
import zipfile
import requests
import re
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
                    # 複数の場所を確認
                    locations = [
                        (winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon"),
                        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
                    ]
                    
                    for hkey, path in locations:
                        try:
                            key = winreg.OpenKey(hkey, path)
                            if "BLBeacon" in path:
                                version, _ = winreg.QueryValueEx(key, "version")
                            else:
                                # chrome.exeのパスから取得を試みる
                                import subprocess
                                exe_path, _ = winreg.QueryValueEx(key, "")
                                result = subprocess.run([exe_path, "--version"], 
                                                      capture_output=True, text=True)
                                if result.returncode == 0:
                                    # "Google Chrome 120.0.6099.129" のような形式から抽出
                                    version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                                    if version_match:
                                        version = version_match.group(1)
                            winreg.CloseKey(key)
                            return version
                        except:
                            continue
                except:
                    pass
                    
            # macOS/Linux - 簡易的に最新の安定版を返す
            return "131.0.6778.204"  # 2025年1月時点の安定版
            
        except Exception as e:
            self.logger.warning(f"Chromeバージョン取得失敗: {e}")
            return "131.0.6778.204"
    
    def _download_chromedriver(self, version: str) -> Path:
        """ChromeDriverをダウンロード"""
        system = platform.system().lower()
        if system == "windows":
            platform_name = "win64"
            filename = "chromedriver-win64.zip"
            executable = "chromedriver.exe"
        elif system == "darwin":
            platform_name = "mac-x64"
            filename = "chromedriver-mac-x64.zip"
            executable = "chromedriver"
        else:
            platform_name = "linux64"
            filename = "chromedriver-linux64.zip"
            executable = "chromedriver"
            
        # ChromeDriver URLを構築
        major_version = version.split('.')[0]
        base_url = "https://storage.googleapis.com/chrome-for-testing-public"
        
        # バージョンに応じたURLを構築
        driver_url = f"{base_url}/{version}/{platform_name}/{filename}"
        
        # ダウンロード先
        zip_path = self.driver_dir / filename
        driver_path = self.driver_dir / executable
        
        # 既にダウンロード済みならスキップ
        if driver_path.exists():
            self.logger.info(f"ChromeDriverは既に存在します: {driver_path}")
            return driver_path
            
        try:
            # まず正確なバージョンでダウンロードを試みる
            urls_to_try = [
                driver_url,
                # バージョンが見つからない場合のフォールバック
                f"{base_url}/LATEST_RELEASE_{major_version}/{platform_name}/{filename}",
                # 最新の安定版
                f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}",
            ]
            
            for url in urls_to_try:
                try:
                    self.logger.info(f"ChromeDriverをダウンロード試行中: {url}")
                    response = requests.get(url, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    # 最新バージョン番号の取得（LATEST_RELEASEの場合）
                    if "LATEST_RELEASE" in url and response.headers.get('content-type', '').startswith('text/'):
                        latest_version = response.text.strip()
                        self.logger.info(f"最新バージョン: {latest_version}")
                        # 新しいURLで再試行
                        driver_url = f"{base_url}/{latest_version}/{platform_name}/{filename}"
                        response = requests.get(driver_url, stream=True, timeout=30)
                        response.raise_for_status()
                    
                    # ファイルをダウンロード
                    with open(zip_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    break
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"ダウンロード失敗: {url} - {e}")
                    continue
            else:
                raise Exception("すべてのダウンロードURLで失敗しました")
                    
            # 解凍
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # chromedriver-win64/chromedriver.exe のような構造の場合に対応
                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith(executable):
                        # ファイル名だけを抽出してドライバーディレクトリに配置
                        target_path = self.driver_dir / executable
                        with zip_ref.open(file_info) as source, open(target_path, 'wb') as target:
                            target.write(source.read())
                        driver_path = target_path
                        break
                        
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