"""エラーチェックの成功・失敗判定を行うモジュール

エラーファイル検知のための判定ロジックを集約
"""
from typing import Tuple, Optional
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path

from utils.logger import get_logger
from utils.config import get_config


class ErrorCheckValidator:
    """エラーチェックの判定を行うクラス"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_config()
        
        # Basic認証情報を取得
        web_config = self.config.get_web_config()
        self.username = web_config.get('username', 'ep_user')
        self.password = web_config.get('password', 'Nn7eUTX5')
        self.auth = HTTPBasicAuth(self.username, self.password)
        
    def validate_pdf_url(self, pdf_url: str, filename: str = "") -> Tuple[bool, str]:
        """
        PDF URLをチェックして、エラーファイルかどうか判定
        
        Args:
            pdf_url: チェックするPDF URL
            filename: ファイル名（ログ用）
            
        Returns:
            (is_error, reason)
            - is_error: True=エラーファイル, False=正常ファイル
            - reason: 判定理由
        """
        try:
            self.logger.info(f"PDF URLチェック開始: {filename}")
            self.logger.debug(f"URL: {pdf_url}")
            
            # 1. URLが空の場合
            if not pdf_url:
                return True, "URLが空です"
            
            # 2. PDF URL形式チェック
            if 'do_download_pdf' not in pdf_url:
                self.logger.warning(f"PDF URLではありません: {pdf_url}")
                return True, "PDF URL形式ではありません"
            
            # 3. Basic認証付きでアクセス
            headers = {
                'User-Agent': 'TechnicalFountainTool/1.0',
                'Accept': 'application/pdf,text/html,*/*'
            }
            
            response = requests.get(
                pdf_url, 
                auth=self.auth,
                headers=headers,
                timeout=30,
                allow_redirects=True
            )
            
            # 4. ステータスコードチェック
            if response.status_code == 401:
                return True, "認証エラー（401）"
            elif response.status_code == 404:
                return True, "ファイルが見つかりません（404）"
            elif response.status_code != 200:
                return True, f"HTTPエラー（{response.status_code}）"
            
            # 5. Content-Typeチェック
            content_type = response.headers.get('Content-Type', '').lower()
            
            # 6. ファイル内容チェック
            content_start = response.content[:1000] if response.content else b''
            
            # 6.1 PDFマジックナンバーチェック（正常）
            if content_start.startswith(b'%PDF'):
                self.logger.info(f"✓ 正常なPDFファイル: {filename}")
                return False, "正常なPDFファイル"
            
            # 6.2 明示的にPDF Content-Typeの場合（正常）
            if 'application/pdf' in content_type and len(response.content) > 100:
                self.logger.info(f"✓ 正常なPDFファイル（Content-Type判定）: {filename}")
                return False, "正常なPDFファイル（Content-Type判定）"
            
            # 6.3 HTMLエラーページチェック（エラー）
            if b'<html' in content_start.lower() or b'<!doctype' in content_start.lower():
                # HTMLの内容を確認
                try:
                    html_content = content_start.decode('utf-8', errors='ignore')
                    
                    # エラーページのキーワード
                    error_keywords = [
                        'ファイルの作成に失敗',
                        'エラーが発生',
                        'PDF生成エラー',
                        'conversion failed',
                        'error occurred'
                    ]
                    
                    for keyword in error_keywords:
                        if keyword in html_content:
                            self.logger.error(f"✗ エラーページ検出: {filename} - {keyword}")
                            return True, f"エラーページ（{keyword}）"
                    
                    # エラーキーワードがなくてもHTMLならエラー
                    self.logger.error(f"✗ HTMLページが返されました: {filename}")
                    return True, "HTMLページが返されました（PDF生成失敗）"
                    
                except Exception as e:
                    self.logger.error(f"HTMLデコードエラー: {e}")
                    return True, "不正なHTMLレスポンス"
            
            # 6.4 空のレスポンス（エラー）
            if len(response.content) == 0:
                self.logger.error(f"✗ 空のレスポンス: {filename}")
                return True, "空のレスポンス"
            
            # 6.5 その他の形式（エラー）
            self.logger.error(f"✗ 不明な形式: {filename}")
            self.logger.debug(f"Content-Type: {content_type}")
            self.logger.debug(f"Content先頭: {content_start[:50]}")
            return True, f"不明な形式（Content-Type: {content_type}）"
            
        except requests.exceptions.Timeout:
            self.logger.error(f"✗ タイムアウト: {filename}")
            return True, "タイムアウト"
        except requests.exceptions.ConnectionError:
            self.logger.error(f"✗ 接続エラー: {filename}")
            return True, "接続エラー"
        except Exception as e:
            self.logger.error(f"✗ 予期しないエラー: {filename} - {e}")
            return True, f"予期しないエラー: {str(e)}"
    
    def validate_batch(self, file_url_map: dict) -> Tuple[list, list]:
        """
        複数ファイルのバッチ検証
        
        Args:
            file_url_map: {ファイル名: PDF URL}の辞書
            
        Returns:
            (error_files, normal_files)
            - error_files: エラーファイルのリスト
            - normal_files: 正常ファイルのリスト
        """
        error_files = []
        normal_files = []
        
        for filename, pdf_url in file_url_map.items():
            is_error, reason = self.validate_pdf_url(pdf_url, filename)
            
            if is_error:
                error_files.append({
                    'filename': filename,
                    'url': pdf_url,
                    'reason': reason
                })
            else:
                normal_files.append({
                    'filename': filename,
                    'url': pdf_url,
                    'reason': reason
                })
        
        return error_files, normal_files