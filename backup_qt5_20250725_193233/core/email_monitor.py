﻿"""メール監視モジュール"""
import imaplib
import email
import re
import time
from typing import Optional
from datetime import datetime, timedelta

from utils.logger import get_logger
from utils.config import get_config


class EmailMonitor:
    """メールを監視してダウンロードURLを取得するクラス"""
    
    def __init__(self, email_address: str, password: str):
        """
        EmailMonitorを初期化
        
        Args:
            email_address: メールアドレス
            password: パスワード（アプリパスワード）
        """
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.email_address = email_address
        self.password = password
        
        # IMAP設定を取得
        email_config = self.config.get_email_config()
        self.imap_server = email_config.get('imap_server', 'imap.gmail.com')
        self.imap_port = email_config.get('imap_port', 993)
        
        self.connection = None
    
    def connect(self):
        """IMAPサーバーに接続"""
        try:
            self.logger.info(f"IMAPサーバーに接続中: {self.imap_server}:{self.imap_port}")
            
            # SSL接続
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            
            # ログイン
            self.connection.login(self.email_address, self.password)
            
            # INBOXを選択
            self.connection.select('INBOX')
            
            self.logger.info("IMAPサーバーへの接続に成功しました")
            
        except imaplib.IMAP4.error as e:
            self.logger.error(f"IMAP接続エラー: {e}")
            raise
        except Exception as e:
            self.logger.error(f"接続中にエラーが発生: {e}")
            raise
    
    def wait_for_email(self, subject_pattern: str = "Re:VIEW to 超原稿用紙", 
                      timeout: int = 600, check_interval: int = 10) -> Optional[str]:
        """
        特定の件名のメールを待機してダウンロードURLを取得
        
        Args:
            subject_pattern: 待機する件名のパターン
            timeout: タイムアウト時間（秒）
            check_interval: チェック間隔（秒）
        
        Returns:
            ダウンロードURL（見つからない場合はNone）
        """
        if not self.connection:
            self.connect()
        
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=timeout)
        
        self.logger.info(f"メール待機開始: 件名 '{subject_pattern}' (タイムアウト: {timeout}秒)")
        
        while datetime.now() < end_time:
            try:
                # 新しいメールを検索
                since_date = start_time.strftime("%d-%b-%Y")
                
                # 日本語を含む検索の場合は特別な処理
                if any(ord(c) > 127 for c in subject_pattern):
                    # UTF-8をサポートするように設定
                    try:
                        # UTF-8検索を有効化（Gmailでサポート）
                        self.connection.literal = subject_pattern.encode('utf-8')
                        search_criteria = f'SINCE "{since_date}" SUBJECT {{{len(self.connection.literal)}}}'
                        typ, data = self.connection.search('UTF-8', search_criteria)
                    except:
                        # UTF-8がサポートされない場合は日付のみで検索
                        self.logger.warning("UTF-8検索がサポートされていません。日付のみで検索します。")
                        search_criteria = f'SINCE "{since_date}"'
                        typ, data = self.connection.search(None, search_criteria)
                else:
                    # ASCII文字のみの場合は通常の検索
                    search_criteria = f'SINCE "{since_date}" SUBJECT "{subject_pattern}"'
                    typ, data = self.connection.search(None, search_criteria)
                
                if typ == 'OK':
                    email_ids = data[0].split()
                    
                    if email_ids:
                        # 新しいメールから順に確認（逆順）
                        for email_id in reversed(email_ids):
                            self.logger.info(f"メールID {email_id} を確認中...")
                            
                            # メールを取得
                            typ, msg_data = self.connection.fetch(email_id, '(RFC822)')
                            
                            if typ == 'OK':
                                # メールを解析
                                raw_email = msg_data[0][1]
                                msg = email.message_from_bytes(raw_email)
                                
                                # 件名を確認
                                subject = msg.get('Subject', '')
                                if subject:
                                    try:
                                        # 件名をデコード
                                        decoded_subject = str(email.header.make_header(email.header.decode_header(subject)))
                                        self.logger.info(f"件名: {decoded_subject}")
                                        
                                        # 件名パターンと一致するか確認
                                        if subject_pattern in decoded_subject:
                                            self.logger.info(f"該当するメールを発見: ID {email_id}, 件名: {decoded_subject}")
                                            
                                            # URLを抽出
                                            download_url = self._extract_download_url(msg)
                                            if download_url:
                                                self.logger.info(f"ダウンロードURLを取得: {download_url}")
                                                return download_url
                                    except Exception as decode_error:
                                        self.logger.warning(f"件名デコードエラー (ID {email_id}): {decode_error}")
                                        # デコードエラーの場合はスキップして次へ
                                        continue
                
                # 次のチェックまで待機
                remaining = (end_time - datetime.now()).total_seconds()
                if remaining > check_interval:
                    self.logger.info(f"次のチェックまで{check_interval}秒待機...")
                    time.sleep(check_interval)
                else:
                    time.sleep(max(1, remaining))
                    
            except Exception as e:
                self.logger.error(f"メール確認中にエラー: {e}")
                # エラー時は少し待ってリトライ
                time.sleep(check_interval)
        
        self.logger.warning(f"タイムアウト: {timeout}秒以内にメールが見つかりませんでした")
        return None
    
    def _extract_download_url(self, msg: email.message.Message) -> Optional[str]:
        """
        メールからダウンロードURLを抽出
        
        Args:
            msg: メールメッセージ
        
        Returns:
            ダウンロードURL（見つからない場合はNone）
        """
        try:
            # メール本文を取得
            body = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            # 複数のエンコーディングを試行
                            body = self._safe_decode_payload(payload)
                            if body:
                                break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = self._safe_decode_payload(payload)
            
            if not body:
                self.logger.warning("メール本文を取得できませんでした")
                return None
            
            # URLパターンを検索
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+\.zip'
            urls = re.findall(url_pattern, body)
            
            if urls:
                # 最初のZIPファイルURLを返す
                return urls[0]
            
            # より一般的なURLパターンも試す
            general_url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            all_urls = re.findall(general_url_pattern, body)
            
            # ダウンロード関連のキーワードを含むURLを探す
            for url in all_urls:
                if any(keyword in url.lower() for keyword in ['download', 'dl', 'file']):
                    return url
            
            self.logger.warning("メール本文からURLが見つかりませんでした")
            return None
            
        except Exception as e:
            self.logger.error(f"URL抽出中にエラー: {e}")
            return None
    
    def _safe_decode_payload(self, payload: bytes) -> str:
        """
        ペイロードを安全にデコード
        
        Args:
            payload: バイトデータ
        
        Returns:
            デコードされた文字列
        """
        # 試行するエンコーディングリスト
        encodings = ['utf-8', 'iso-2022-jp', 'shift_jis', 'euc-jp', 'ascii']
        
        for encoding in encodings:
            try:
                return payload.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                continue
        
        # すべて失敗した場合はエラーを無視してデコード
        try:
            return payload.decode('utf-8', errors='ignore')
        except Exception:
            self.logger.warning("ペイロードのデコードに失敗しました")
            return ""
    
    def close(self):
        """接続を閉じる"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                self.logger.info("IMAP接続を閉じました")
            except:
                pass