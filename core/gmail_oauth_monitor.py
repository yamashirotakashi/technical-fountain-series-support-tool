"""Gmail API OAuth2.0認証を使用したメール監視モジュール"""
from __future__ import annotations

import base64
import json
import os
import pickle
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Tuple, List, Dict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.logger import get_logger
from utils.config import get_config
from core.email_processors import EmailProcessor, create_email_processor


class GmailOAuthMonitor:
    """Gmail API OAuth2.0認証を使用してメールを監視するクラス"""
    
    def __init__(self, credentials_path: str = None, service_type: str = 'word2xhtml5'):
        """
        Gmail OAuth Monitor を初期化
        
        Args:
            credentials_path: OAuth2.0クライアント認証ファイルのパス
            service_type: 'word2xhtml5' または 'review'
        """
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.service_type = service_type
        self.email_processor = create_email_processor(service_type)
        
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
                # デフォルトの送信者は指定しない（呼び出し元で明示的に指定すべき）
                pass
            
            if since_time:
                # Gmail検索では秒単位の精度で時刻指定可能
                epoch_timestamp = int(since_time.timestamp())
                
                # デバッグ: 現在時刻も確認
                import time
                current_timestamp = int(time.time())
                self.logger.info(f"検索対象: {since_time.isoformat()}以降のメール")
                self.logger.info(f"エポックタイムスタンプ: {epoch_timestamp} (現在: {current_timestamp})")
                
                # より正確な時刻フィルタリング
                # Gmail APIのafter:はUNIXタイムスタンプまたは日付形式をサポート
                # 秒単位の精度で検索するためにタイムスタンプを使用
                query_parts.append(f'after:{epoch_timestamp}')
                self.logger.info(f"実際の検索タイムスタンプ: {epoch_timestamp} ({since_time.strftime('%Y-%m-%d %H:%M:%S UTC')})")
            
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
    
    def extract_download_url_and_filename(self, message: Dict, 
                                         purpose: str = 'download') -> Optional[Tuple[str, str]]:
        """
        メッセージからダウンロードURLとファイル名を抽出
        
        Args:
            message: Gmail APIから取得したメッセージ
            purpose: 'download' または 'error_check'
            
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
            
            # EmailProcessorを使用してURLを抽出
            urls = self.email_processor.extract_urls(body_text)
            if not urls:
                self.logger.warning("URLが見つかりませんでした")
                return None
            
            # 目的に応じたURLを取得
            download_url = self.email_processor.get_url_for_purpose(urls, purpose)
            if not download_url:
                self.logger.warning(f"目的 '{purpose}' に適したURLが見つかりませんでした")
                return None
            
            # ファイル名を抽出
            filename = self.email_processor.extract_filename(body_text)
            
            if filename:
                return (download_url, filename)
            else:
                # ファイル名が見つからない場合はデフォルト名を使用
                self.logger.warning("ファイル名が見つかりませんでした。デフォルト名を使用します。")
                default_name = "converted.zip" if purpose == 'download' else "converted.pdf"
                return (download_url, default_name)
            
        except Exception as e:
            self.logger.error(f"URL/ファイル名抽出エラー: {e}")
            return None
    
    def extract_pdf_url_from_message(self, message: Dict) -> Optional[str]:
        """
        メッセージからPDF URLのみを抽出（エラーファイル検知用）
        
        Args:
            message: Gmail APIから取得したメッセージ
            
        Returns:
            PDF URL または None
        """
        try:
            # メール本文を取得
            payload = message.get('payload', {})
            body_text = self._extract_body_text(payload)
            
            if not body_text:
                return None
            
            self.logger.info("エラーファイル検知用にPDF URLを抽出中...")
            
            # すべてのURLを抽出
            all_urls = []
            
            # PDF URLパターン
            pdf_url_patterns = [
                r'http://trial\.nextpublishing\.jp/upload_46tate/do_download_pdf\?n=[^\s\n\r<>"]+',
                r'http://trial\.nextpublishing\.jp/rapture/do_download_pdf\?n=[^\s\n\r<>"]+',
            ]
            
            for pattern in pdf_url_patterns:
                matches = re.findall(pattern, body_text)
                if matches:
                    all_urls.extend(matches)
                    self.logger.info(f"PDF URLパターン {pattern} で {len(matches)} 件のURLを発見")
            
            if all_urls:
                # 最後のPDF URLを返す（ユーザーの指示により）
                self.logger.info(f"見つかったPDF URL数: {len(all_urls)}件")
                self.logger.info(f"最後のPDF URLを使用: {all_urls[-1]}")
                return all_urls[-1]
            else:
                self.logger.warning("PDF URLが見つかりませんでした")
                # デバッグ用：メール本文の一部を表示
                self.logger.debug(f"メール本文（最初の1000文字）: {body_text[:1000]}")
                return None
            
        except Exception as e:
            self.logger.error(f"PDF URL抽出エラー: {e}")
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
                      from_address: Optional[str] = None,
                      purpose: str = 'download') -> Optional[Tuple[str, str]]:
        """
        特定の件名のメールを待機してダウンロードURLを取得
        
        Args:
            subject_pattern: 待機する件名のパターン
            since_time: この時刻以降のメールのみ検索
            timeout: タイムアウト時間（秒）
            check_interval: チェック間隔（秒）
            from_address: 送信元メールアドレス（フィルタリング用）
            purpose: 'download' または 'error_check' - 用途に応じたURLを抽出
        
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
                for idx, message in enumerate(messages):
                    message_id = message['id']
                    self.logger.info(f"メール {idx+1}/{len(messages)} を処理中: ID={message_id}")
                    
                    if message_id in processed_message_ids:
                        self.logger.info(f"既に処理済みのメール: {message_id}")
                        continue
                    
                    # メッセージの詳細を取得
                    message_details = self.get_message_details(message_id)
                    if not message_details:
                        self.logger.warning(f"メッセージ詳細を取得できませんでした: {message_id}")
                        continue
                    
                    # メールの受信時刻を確認（since_timeが指定されている場合）
                    if since_time:
                        internal_date = message_details.get('internalDate')
                        if internal_date:
                            # internalDateはミリ秒単位のUNIXタイムスタンプ
                            email_timestamp = int(internal_date) / 1000
                            email_datetime = datetime.fromtimestamp(email_timestamp, tz=timezone.utc)
                            
                            # 時刻比較のログ
                            from zoneinfo import ZoneInfo
                            jst = ZoneInfo('Asia/Tokyo')
                            email_jst = email_datetime.astimezone(jst)
                            since_jst = since_time.astimezone(jst)
                            
                            self.logger.info(f"メール受信時刻(UTC): {email_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                            self.logger.info(f"メール受信時刻(JST): {email_jst.strftime('%Y-%m-%d %H:%M:%S')}")
                            self.logger.info(f"検索基準時刻(JST): {since_jst.strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            # since_timeより前のメールはスキップ
                            if email_datetime < since_time:
                                time_diff = (since_time - email_datetime).total_seconds()
                                self.logger.info(f"古いメールをスキップ: {int(time_diff)}秒前のメール")
                                processed_message_ids.add(message_id)
                                continue
                    
                    # URLとファイル名を抽出（purposeパラメータを渡す）
                    result = self.extract_download_url_and_filename(message_details, purpose=purpose)
                    if result:
                        url, filename = result
                        self.logger.info(f"メール検出（{purpose}）: {filename} -> {url}")
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