"""Gmail APIを使用したメール監視モジュール"""
from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, List, Dict
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.logger import get_logger
from utils.config import get_config


class GmailAPIMonitor:
    """Gmail APIを使用してメールを監視するクラス"""
    
    def __init__(self, credentials_path: str = None):
        """
        Gmail API Monitorを初期化
        
        Args:
            credentials_path: サービスアカウント認証ファイルのパス
        """
        self.logger = get_logger(__name__)
        self.config = get_config()
        
        # 認証設定
        if not credentials_path:
            credentials_path = self.config.get_google_sheet_config().get('credentials_path')
        
        self.credentials_path = credentials_path
        self.service = None
        self.user_email = self.config.get_email_config().get('default_address', 'yamashiro.takashi@gmail.com')
        
        # Gmail APIスコープ（読み取り専用）
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def authenticate(self):
        """Gmail APIに認証"""
        try:
            self.logger.info("Gmail API認証を開始")
            
            # サービスアカウント認証
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.scopes
            )
            
            # ユーザーを委任（Domain-wide delegation）
            delegated_credentials = credentials.with_subject(self.user_email)
            
            # Gmail APIサービスを構築
            self.service = build('gmail', 'v1', credentials=delegated_credentials)
            
            self.logger.info(f"Gmail API認証成功: {self.user_email}")
            
        except Exception as e:
            self.logger.error(f"Gmail API認証エラー: {e}")
            raise
    
    def search_emails(self, 
                     subject_pattern: str = "ダウンロード用URLのご案内",
                     since_time: Optional[datetime] = None,
                     max_results: int = 10) -> List[Dict]:
        """
        メールを検索
        
        Args:
            subject_pattern: 件名パターン
            since_time: この時刻以降のメール
            max_results: 最大取得件数
            
        Returns:
            メールのリスト
        """
        if not self.service:
            self.authenticate()
        
        try:
            # 検索クエリを構築
            query_parts = [f'subject:"{subject_pattern}"']
            
            if since_time:
                # Gmail検索では秒単位の精度で時刻指定可能
                epoch_timestamp = int(since_time.timestamp())
                query_parts.append(f'after:{epoch_timestamp}')
                self.logger.info(f"検索対象: {since_time.isoformat()}以降のメール")
            
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
            
            self.logger.debug(f"メール本文（先頭500文字）: {body_text[:500]}")
            
            # ダウンロードURLを抽出
            url_patterns = [
                r'http://trial\.nextpublishing\.jp/upload_46tate/do_download\?n=[^\\s\\n\\r]+',
                r'<(http://trial\.nextpublishing\.jp/upload_46tate/do_download\?[^>]+)>',
            ]
            
            download_url = None
            for pattern in url_patterns:
                url_match = re.search(pattern, body_text)
                if url_match:
                    download_url = url_match.group(1) if url_match.lastindex else url_match.group(0)
                    break
            
            # ファイル名を抽出
            filename_patterns = [
                r'ファイル名：([^\\n\\r]+\\.docx)',
                r'ファイル名：([^\\n\\r]+)',
                r'ファイル：([^\\n\\r]+\\.docx)',
                r'([^\\s]+\\.docx)'
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
                      since_time: Optional[datetime] = None,
                      timeout: int = 600,
                      check_interval: int = 10) -> Optional[Tuple[str, str]]:
        """
        特定の件名のメールを待機してダウンロードURLを取得
        
        Args:
            subject_pattern: 待機する件名のパターン
            since_time: この時刻以降のメールのみ検索
            timeout: タイムアウト時間（秒）
            check_interval: チェック間隔（秒）
        
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
                    max_results=50
                )
                
                # 新しいメッセージをチェック
                for message in messages:
                    message_id = message['id']
                    
                    if message_id in processed_message_ids:
                        continue
                    
                    # メッセージの詳細を取得
                    message_details = self.get_message_details(message_id)
                    if not message_details:
                        continue
                    
                    # URLとファイル名を抽出
                    result = self.extract_download_url_and_filename(message_details)
                    if result:
                        url, filename = result
                        self.logger.info(f"メール検出: {filename} -> {url}")
                        return result
                    
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


def test_gmail_api():
    """Gmail APIテスト関数"""
    monitor = GmailAPIMonitor()
    
    try:
        # 認証テスト
        monitor.authenticate()
        print("✅ Gmail API認証成功")
        
        # 最近のメール検索テスト
        since_time = datetime.now() - timedelta(hours=1)
        messages = monitor.search_emails(since_time=since_time, max_results=5)
        print(f"✅ メール検索成功: {len(messages)}件")
        
        # メッセージ詳細取得テスト
        if messages:
            message_details = monitor.get_message_details(messages[0]['id'])
            if message_details:
                print("✅ メッセージ詳細取得成功")
                
                # URL/ファイル名抽出テスト
                result = monitor.extract_download_url_and_filename(message_details)
                if result:
                    url, filename = result
                    print(f"✅ URL/ファイル名抽出成功: {filename}")
                else:
                    print("⚠️ URL/ファイル名抽出失敗（該当メールなし）")
        
    except Exception as e:
        print(f"❌ Gmail APIテストエラー: {e}")


if __name__ == "__main__":
    test_gmail_api()