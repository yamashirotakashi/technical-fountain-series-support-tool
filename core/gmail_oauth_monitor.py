"""Gmail API OAuth2.0認証を使用したメール監視モジュール"""

import base64
import json
import os
import pickle
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, List, Dict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.logger import get_logger
from utils.config import get_config


class GmailOAuthMonitor:
    """Gmail API OAuth2.0認証を使用してメールを監視するクラス"""
    
    def __init__(self, credentials_path: str = None):
        """
        Gmail OAuth Monitor を初期化
        
        Args:
            credentials_path: OAuth2.0クライアント認証ファイルのパス
        """
        self.logger = get_logger(__name__)
        self.config = get_config()
        
        # EXE環境対応
        from core.gmail_oauth_exe_helper import gmail_oauth_helper
        self.exe_helper = gmail_oauth_helper
        
        # 認証設定（EXE環境対応）
        if credentials_path:
            self.credentials_path = credentials_path
            self.token_path = str(Path(credentials_path).parent / "gmail_token.pickle")
        else:
            self.credentials_path, self.token_path = self.exe_helper.get_credentials_path()
        
        self.service = None
        
        # Gmail APIスコープ（読み取り専用）
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def authenticate(self):
        """Gmail APIにOAuth2.0で認証"""
        creds = None
        
        # 既存のトークンファイルを確認
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # 認証情報が無効または存在しない場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info("Gmail API認証をリフレッシュしました")
                except Exception as e:
                    self.logger.warning(f"認証リフレッシュ失敗: {e}")
                    creds = None
            
            if not creds:
                # 新規OAuth2.0フロー
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"OAuth2.0認証ファイルが見つかりません: {self.credentials_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.scopes)
                # EXE環境対応のポート設定
                port = self.exe_helper.get_oauth_port()
                creds = flow.run_local_server(port=port)
                self.logger.info("新しいOAuth2.0認証を完了しました")
            
            # トークンを保存
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Gmail APIサービスを構築
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Gmail API認証成功")
    
    def search_emails(self, 
                     subject_pattern: str = "ダウンロード用URLのご案内",
                     since_time: Optional[datetime] = None,
                     max_results: int = 10,
                     from_address: Optional[str] = None) -> List[Dict]:
        """
        メールを検索
        
        Args:
            subject_pattern: 件名パターン
            since_time: この時刻以降のメール
            max_results: 最大取得件数
            from_address: 送信元メールアドレス（フィルタリング用）
            
        Returns:
            メールのリスト
        """
        if not self.service:
            self.authenticate()
        
        try:
            # 検索クエリを構築
            query_parts = [f'subject:"{subject_pattern}"']
            
            # Re:VIEW処理用の送信元フィルタを追加
            if from_address:
                query_parts.append(f'from:{from_address}')
            else:
                # デフォルトでRe:VIEW処理のメールアドレスを使用
                # ※ エラーチェック用のメールは除外
                query_parts.append('from:kanazawa@nextpublishing.jp')
            
            if since_time:
                # Gmail検索では秒単位の精度で時刻指定可能
                epoch_timestamp = int(since_time.timestamp())
                
                # デバッグ: 現在時刻も確認
                import time
                current_timestamp = int(time.time())
                self.logger.info(f"検索対象: {since_time.isoformat()}以降のメール")
                self.logger.info(f"エポックタイムスタンプ: {epoch_timestamp} (現在: {current_timestamp})")
                
                # 5分前からの検索に変更（メール配送の遅延を考慮）
                search_timestamp = epoch_timestamp - 300  # 5分前
                query_parts.append(f'after:{search_timestamp}')
                self.logger.info(f"実際の検索タイムスタンプ: {search_timestamp} (5分前から検索)")
            
            query = ' '.join(query_parts)
            self.logger.info(f"Gmail検索クエリ: {query}")
            
            # メールを検索
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = result.get('messages', [])
            self.logger.info(f"検索結果: {len(messages)}件のメール")
            
            return messages
            
        except HttpError as e:
            self.logger.error(f"Gmail検索エラー: {e}")
            return []
    
    def get_message_details(self, message_id: str) -> Optional[Dict]:
        """
        メッセージの詳細を取得
        
        Args:
            message_id: メッセージID
            
        Returns:
            メッセージの詳細情報
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            return message
            
        except HttpError as e:
            self.logger.error(f"メッセージ取得エラー: {e}")
            return None
    
    def extract_download_url_and_filename(self, message: Dict) -> Optional[Tuple[str, str]]:
        """
        メッセージからダウンロードURLとファイル名を抽出
        
        Args:
            message: Gmail APIから取得したメッセージ
            
        Returns:
            (ダウンロードURL, ファイル名) または None
        """
        try:
            # メール本文を取得
            payload = message.get('payload', {})
            body_text = self._extract_body_text(payload)
            
            if not body_text:
                return None
            
            self.logger.info(f"メール本文（先頭500文字）: {body_text[:500]}")
            self.logger.debug(f"メール本文全体の長さ: {len(body_text)}文字")
            
            # まず、ZIPファイルのダウンロードURLを探す（do_download）
            # ※ do_download_pdfは個別ファイル用なので除外
            zip_url_patterns = [
                # ZIPファイル用のダウンロードURL（do_download）を優先
                r'http://trial\.nextpublishing\.jp/rapture/do_download\?n=[^\s\n\r]+',
                r'http://trial\.nextpublishing\.jp/upload_46tate/do_download\?n=[^\s\n\r]+',
                r'<(http://trial\.nextpublishing\.jp/[^/]+/do_download\?[^>]+)>',
                # ReVIEW形式用のダウンロードURL
                r'http://trial\.nextpublishing\.jp/upload_46tate/do_download_review\?n=[^\s\n\r]+',
            ]
            
            download_url = None
            url_type = None
            for pattern in zip_url_patterns:
                url_match = re.search(pattern, body_text)
                if url_match:
                    download_url = url_match.group(1) if url_match.lastindex else url_match.group(0)
                    if 'do_download_review' in download_url:
                        url_type = "ReVIEW形式"
                    else:
                        url_type = "ZIP形式"
                    self.logger.info(f"{url_type}ダウンロードURL抽出: {download_url[:80]}...")
                    break
                else:
                    self.logger.debug(f"パターン {pattern} にマッチしませんでした")
            
            # ZIPファイルのURLが見つからない場合は、個別PDFのURLも探す（フォールバック）
            if not download_url:
                pdf_url_patterns = [
                    r'http://trial\.nextpublishing\.jp/upload_46tate/do_download_pdf\?n=[^\s\n\r]+',
                    r'<(http://trial\.nextpublishing\.jp/upload_46tate/do_download_pdf\?[^>]+)>',
                ]
                
                for pattern in pdf_url_patterns:
                    url_match = re.search(pattern, body_text)
                    if url_match:
                        download_url = url_match.group(1) if url_match.lastindex else url_match.group(0)
                        self.logger.warning(f"ZIP URLが見つからないため、PDF URLを使用: {download_url[:80]}...")
                        break
            
            # ファイル名を抽出
            filename_patterns = [
                # ZIPファイル名のパターン
                r'ファイル名：([^\n\r]+\.zip)',
                r'([^\s]+\.zip)',
                # 従来のdocxパターン（フォールバック）
                r'ファイル名：([^\n\r]+\.docx)',
                r'ファイル名：([^\n\r]+)',
                r'ファイル：([^\n\r]+\.docx)',
                r'([^\s]+\.docx)',
                # 実際のメール形式に対応
                r'超原稿用紙\s*\n\s*([^\n\r]+\.docx)',
                r'アップロードしていただいた[^\n]*\n\s*([^\n\r]+\.docx)',
            ]
            
            filename = None
            for pattern in filename_patterns:
                filename_match = re.search(pattern, body_text)
                if filename_match:
                    filename = filename_match.group(1).strip()
                    self.logger.info(f"メール本文からファイル名を検出: {filename}")
                    break
            
            if download_url and filename:
                return (download_url, filename)
            elif download_url:
                # ファイル名が見つからない場合はデフォルト名を使用
                self.logger.warning("ファイル名が見つかりませんでした。デフォルト名を使用します。")
                return (download_url, "converted.zip")
            
            return None
            
        except Exception as e:
            self.logger.error(f"URL/ファイル名抽出エラー: {e}")
            return None
    
    def _extract_body_text(self, payload: Dict) -> str:
        """メールペイロードから本文テキストを抽出"""
        body_text = ""
        
        # マルチパートメッセージの場合
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data')
                    if data:
                        # Base64デコード
                        decoded_data = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        body_text += decoded_data
                elif 'parts' in part:
                    # 再帰的に処理
                    body_text += self._extract_body_text(part)
        else:
            # シンプルメッセージの場合
            if payload.get('mimeType') == 'text/plain':
                data = payload.get('body', {}).get('data')
                if data:
                    body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return body_text
    
    def wait_for_email(self, 
                      subject_pattern: str = "ダウンロード用URLのご案内",
                      timeout: int = 600,
                      check_interval: int = 10,
                      return_with_filename: bool = False,
                      since_time: Optional[datetime] = None,
                      from_address: Optional[str] = None) -> Optional[Tuple[str, str]]:
        """
        特定の件名のメールを待機してダウンロードURLを取得
        
        Args:
            subject_pattern: 待機する件名のパターン
            since_time: この時刻以降のメールのみ検索
            timeout: タイムアウト時間（秒）
            check_interval: チェック間隔（秒）
            from_address: 送信元メールアドレス（フィルタリング用）
        
        Returns:
            (ダウンロードURL, ファイル名) または None
        """
        if not self.service:
            self.authenticate()
        
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=timeout)
        
        self.logger.info(f"Gmail APIメール待機開始: 件名 '{subject_pattern}' (タイムアウト: {timeout}秒)")
        if since_time:
            self.logger.info(f"検索対象: {since_time.isoformat()}以降のメール")
        
        processed_message_ids = set()
        
        while datetime.now() < end_time:
            try:
                # メールを検索
                messages = self.search_emails(
                    subject_pattern=subject_pattern,
                    since_time=since_time,
                    max_results=50,
                    from_address=from_address
                )
                
                # 新しいメッセージをチェック
                for message in messages:
                    message_id = message['id']
                    
                    if message_id in processed_message_ids:
                        continue
                    
                    # メッセージの詳細を取得
                    message_details = self.get_message_details(message_id)
                    if not message_details:
                        self.logger.warning(f"メッセージ詳細を取得できませんでした: {message_id}")
                        continue
                    
                    # URLとファイル名を抽出
                    result = self.extract_download_url_and_filename(message_details)
                    if result:
                        url, filename = result
                        self.logger.info(f"メール検出: {filename} -> {url}")
                        # return_with_filenameに関係なく常にタプルで返す（IMAP互換）
                        if return_with_filename:
                            return result
                        else:
                            return url  # 単一のURLを返す場合
                    else:
                        self.logger.warning(f"URLを抽出できませんでした: メッセージID {message_id}")
                    
                    processed_message_ids.add(message_id)
                
                # 指定間隔で待機
                import time
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"Gmail APIメール監視エラー: {e}")
                import time
                time.sleep(check_interval)
        
        self.logger.warning(f"タイムアウト: {timeout}秒間メールが見つかりませんでした")
        return None
    
    def reset_processed_emails(self):
        """IMAP互換性のためのダミーメソッド（Gmail APIでは処理済みID管理が不要）"""
        self.logger.debug("Gmail API: reset_processed_emails (何もしません)")
        pass
    
    def close(self):
        """接続を閉じる（IMAP互換性のため）"""
        # Gmail APIはHTTPSベースのため特別なクローズ処理は不要
        # IMAPMonitorとの互換性のために空のメソッドを提供
        if self.service:
            self.logger.debug("Gmail API接続を終了しました")
        pass


def setup_oauth_credentials():
    """OAuth2.0認証ファイルのセットアップガイド"""
    print("🔐 Gmail API OAuth2.0認証設定ガイド")
    print("=" * 60)
    print()
    print("1. Google Cloud Console にアクセス")
    print("   https://console.cloud.google.com/")
    print()
    print("2. APIs & Services > Credentials")
    print()
    print("3. 「+ CREATE CREDENTIALS」> OAuth client ID")
    print()
    print("4. Application type: Desktop application")
    print("   Name: TechZip Gmail Monitor")
    print()
    print("5. ダウンロードしたJSONファイルを以下に保存:")
    print("   config/gmail_oauth_credentials.json")
    print()
    print("=" * 60)


if __name__ == "__main__":
    setup_oauth_credentials()