"""Web連携モジュール"""
import os
from pathlib import Path
from typing import Optional, Tuple
import requests
from requests.auth import HTTPBasicAuth

from utils.logger import get_logger
from utils.config import get_config


class WebClient:
    """Webサービスとの連携を管理するクラス"""
    
    def __init__(self):
        """WebClientを初期化"""
        self.logger = get_logger(__name__)
        self.config = get_config()
        
        # Web設定を取得
        web_config = self.config.get_web_config()
        self.base_url = web_config.get('upload_url')
        self.username = web_config.get('username')
        self.password = web_config.get('password')
        
        # HTTPセッションを作成
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(self.username, self.password)
        
        # デフォルトヘッダーを設定
        self.session.headers.update({
            'User-Agent': 'TechnicalFountainTool/1.0'
        })
    
    def upload_file(self, file_path: Path, email: str) -> bool:
        """
        ファイルをアップロード
        
        Args:
            file_path: アップロードするファイルのパス
            email: 通知先メールアドレス
        
        Returns:
            アップロードが成功した場合True
        """
        try:
            self.logger.info(f"ファイルアップロード開始: {file_path}")
            
            if not file_path.exists():
                self.logger.error(f"ファイルが存在しません: {file_path}")
                return False
            
            # フォームデータを準備
            data = {
                'mail': email,
                'mailconf': email
            }
            
            # ファイルを準備
            with open(file_path, 'rb') as f:
                files = {
                    'userfile': (file_path.name, f, 'application/zip')
                }
                
                # POSTリクエストを送信
                self.logger.info(f"アップロード先: {self.base_url}")
                response = self.session.post(
                    self.base_url,
                    data=data,
                    files=files,
                    timeout=300  # 5分のタイムアウト
                )
            
            # レスポンスを確認
            if response.status_code == 200:
                self.logger.info("ファイルアップロードに成功しました")
                self.logger.debug(f"レスポンス: {response.text[:500]}...")
                return True
            else:
                self.logger.error(f"アップロードに失敗: HTTP {response.status_code}")
                self.logger.error(f"レスポンス: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.logger.error("アップロードがタイムアウトしました")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"リクエストエラー: {e}")
            return False
        except Exception as e:
            self.logger.error(f"アップロード中にエラーが発生: {e}")
            return False
    
    def download_file(self, url: str, save_path: Path) -> bool:
        """
        ファイルをダウンロード
        
        Args:
            url: ダウンロードURL
            save_path: 保存先パス
        
        Returns:
            ダウンロードが成功した場合True
        """
        try:
            self.logger.info(f"ファイルダウンロード開始: {url}")
            
            # ディレクトリが存在しない場合は作成
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # GETリクエストでダウンロード（ストリーミング）
            response = self.session.get(
                url,
                stream=True,
                timeout=300
            )
            
            # レスポンスを確認
            if response.status_code == 200:
                # ファイルに書き込み
                total_size = int(response.headers.get('content-length', 0))
                self.logger.info(f"ダウンロードサイズ: {total_size:,} bytes")
                
                downloaded = 0
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 進捗をログ（10%ごと）
                            if total_size > 0:
                                progress = int((downloaded / total_size) * 100)
                                if progress % 10 == 0 and progress != getattr(self, '_last_progress', -1):
                                    self.logger.info(f"ダウンロード進捗: {progress}%")
                                    self._last_progress = progress
                
                self.logger.info(f"ダウンロード完了: {save_path}")
                
                # ダウンロードしたファイルの情報をログ
                file_size = save_path.stat().st_size
                self.logger.info(f"保存されたファイルサイズ: {file_size:,} bytes")
                
                # 最初の数バイトを確認してファイルタイプを判定
                with open(save_path, 'rb') as f:
                    header = f.read(100)
                    # ZIPファイルのマジックナンバー: PK (0x504B)
                    if header.startswith(b'PK'):
                        self.logger.info("ファイルタイプ: ZIP形式")
                    # HTMLの可能性
                    elif header.lower().startswith(b'<!doctype') or header.lower().startswith(b'<html'):
                        self.logger.warning("ファイルタイプ: HTML形式（エラーページの可能性）")
                        # HTMLの内容の一部をログ
                        try:
                            content = save_path.read_text(encoding='utf-8', errors='ignore')[:500]
                            self.logger.warning(f"HTML内容の冒頭: {content}")
                        except:
                            pass
                    else:
                        # 最初の100バイトを16進数で表示
                        hex_header = header[:50].hex()
                        self.logger.warning(f"不明なファイルタイプ。ヘッダー: {hex_header}")
                
                return True
            else:
                self.logger.error(f"ダウンロードに失敗: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            self.logger.error("ダウンロードがタイムアウトしました")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"リクエストエラー: {e}")
            return False
        except Exception as e:
            self.logger.error(f"ダウンロード中にエラーが発生: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        接続をテスト
        
        Returns:
            接続が成功した場合True
        """
        try:
            self.logger.info("Web接続テスト開始")
            
            # HEADリクエストでテスト
            response = self.session.head(
                self.base_url,
                timeout=10
            )
            
            # 認証が必要なサイトの場合、401以外は成功とみなす
            if response.status_code != 401:
                self.logger.info(f"接続テスト成功: HTTP {response.status_code}")
                return True
            else:
                self.logger.error("認証に失敗しました")
                return False
                
        except Exception as e:
            self.logger.error(f"接続テストに失敗: {e}")
            return False
    
    def close(self):
        """セッションを閉じる"""
        self.session.close()
        self.logger.info("HTTPセッションを閉じました")