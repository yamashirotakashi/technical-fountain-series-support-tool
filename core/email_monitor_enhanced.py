"""拡張メール監視モジュール（Word2XHTML5対応）"""
import imaplib
import email
import re
import time
from typing import Optional, Set
from datetime import datetime, timedelta

from utils.logger import get_logger
from utils.config import get_config


class EmailMonitorEnhanced:
    """メールを監視してダウンロードURLを取得するクラス（改良版）"""
    
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
        self.processed_email_ids: Set[bytes] = set()  # 処理済みメールIDを記録
        self.monitoring_start_time = None  # 監視開始時刻
    
    def connect(self):
        """IMAPサーバーに接続"""
        try:
            self.logger.info(f"IMAPサーバーに接続中: {self.imap_server}:{self.imap_port}")
            
            # SSL接続
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            
            # ログイン
            self.connection.login(self.email_address, self.password)
            
            # INBOXを選択
            select_result = self.connection.select('INBOX')
            self.logger.info(f"INBOX選択結果: {select_result}")
            
            self.logger.info("IMAPサーバーへの接続に成功しました")
            
        except imaplib.IMAP4.error as e:
            self.logger.error(f"IMAP接続エラー: {e}")
            raise
        except Exception as e:
            self.logger.error(f"接続中にエラーが発生: {e}")
            raise
    
    def start_monitoring(self):
        """監視を開始（アップロード後に呼び出す）"""
        # タイムゾーン付きの現在時刻を取得
        from datetime import timezone
        self.monitoring_start_time = datetime.now(timezone.utc)
        self.processed_email_ids.clear()
        self.logger.info(f"メール監視開始時刻: {self.monitoring_start_time}")
    
    def wait_for_email(self, subject_pattern: str = "ダウンロード用URLのご案内", 
                      timeout: int = 1200, check_interval: int = 30,
                      file_stem: Optional[str] = None,
                      sender_pattern: str = "support-np@impress.co.jp") -> Optional[str]:
        """
        特定の件名のメールを待機してダウンロードURLを取得
        
        Args:
            subject_pattern: 待機する件名のパターン
            timeout: タイムアウト時間（秒）
            check_interval: チェック間隔（秒）
            file_stem: 対象ファイル名（拡張子なし）
        
        Returns:
            ダウンロードURL（見つからない場合はNone）
        """
        if not self.connection:
            self.connect()
        
        if not self.monitoring_start_time:
            self.start_monitoring()
        
        from datetime import timezone
        end_time = datetime.now(timezone.utc) + timedelta(seconds=timeout)
        
        self.logger.info(f"メール待機開始: 件名 '{subject_pattern}' (タイムアウト: {timeout}秒)")
        if file_stem:
            self.logger.info(f"対象ファイル: {file_stem}")
        
        while datetime.now(timezone.utc) < end_time:
            try:
                # 送信元からのメールをすべて検索
                if sender_pattern:
                    search_criteria = f'FROM "{sender_pattern}"'
                    self.logger.info(f"検索条件: {search_criteria} （送信元のみで検索）")
                else:
                    # 送信元が指定されていない場合は未読メールを検索
                    search_criteria = 'UNSEEN'
                    self.logger.info(f"検索条件: {search_criteria} （未読メールを検索）")
                
                typ, data = self.connection.search(None, search_criteria)
                
                if typ == 'OK':
                    email_ids = data[0].split()
                    self.logger.info(f"検索結果: {len(email_ids)}件のメールが見つかりました")
                    
                    if email_ids:
                        # 新しいメールから順に確認（逆順）
                        for email_id in reversed(email_ids):
                            # 既に処理済みのメールはスキップ
                            if email_id in self.processed_email_ids:
                                self.logger.info(f"メールID {email_id} は既に処理済みです")
                                continue
                            
                            self.logger.info(f"新しいメールID {email_id} を確認中...")
                            
                            # メールを取得
                            typ, msg_data = self.connection.fetch(email_id, '(RFC822)')
                            
                            if typ == 'OK':
                                # メールを解析
                                try:
                                    raw_email = msg_data[0][1]
                                    msg = email.message_from_bytes(raw_email)
                                except Exception as parse_error:
                                    self.logger.error(f"メール解析エラー (ID {email_id}): {parse_error}")
                                    self.processed_email_ids.add(email_id)
                                    continue
                                
                                # デバッグ: メールの基本情報を表示
                                try:
                                    # 生の件名を取得
                                    raw_subject = msg.get('Subject', 'No Subject')
                                    sender = msg.get('From', 'No Sender')
                                    date = msg.get('Date', 'No Date')
                                    
                                    # 件名をデコード
                                    decoded_subject = 'デコード失敗'
                                    try:
                                        decoded_subject = str(email.header.make_header(email.header.decode_header(raw_subject)))
                                    except:
                                        decoded_subject = raw_subject
                                    
                                    self.logger.info(f"=== メール詳細 (ID: {email_id}) ===")
                                    self.logger.info(f"  件名: {decoded_subject}")
                                    self.logger.info(f"  送信元: {sender}")
                                    self.logger.info(f"  日付: {date}")
                                    self.logger.info(f"=================================")
                                except Exception as debug_error:
                                    self.logger.warning(f"デバッグ情報取得エラー: {debug_error}")
                                
                                # メール日時を確認（ログ出力のみ）
                                email_date = self._get_email_date(msg)
                                if email_date:
                                    self.logger.info(f"メール日時: {email_date}")
                                
                                # 日付によるフィルタリングは無効化（コメントアウト）
                                # if email_date and self.monitoring_start_time:
                                #     # 両方の日時をUTCに変換して比較
                                #     from datetime import timezone
                                #     # email_dateがnaiveの場合はUTCとして扱う
                                #     if email_date.tzinfo is None:
                                #         email_date = email_date.replace(tzinfo=timezone.utc)
                                #     # monitoring_start_timeがnaiveの場合もUTCとして扱う
                                #     monitoring_time = self.monitoring_start_time
                                #     if monitoring_time.tzinfo is None:
                                #         monitoring_time = monitoring_time.replace(tzinfo=timezone.utc)
                                #     
                                #     if email_date < monitoring_time:
                                #         # 監視開始前のメールはスキップ
                                #         self.processed_email_ids.add(email_id)
                                #         continue
                                
                                # 送信元を確認
                                sender = msg.get('From', '')
                                self.logger.info(f"送信元: {sender}")
                                
                                # 送信元パターンと一致するか確認
                                if sender_pattern and sender_pattern not in sender:
                                    self.logger.info(f"送信元が期待値と異なります（期待: {sender_pattern}）")
                                    self.processed_email_ids.add(email_id)
                                    continue
                                
                                # 件名を確認
                                subject = msg.get('Subject', '')
                                if subject:
                                    try:
                                        # 件名をデコード
                                        decoded_subject = str(email.header.make_header(email.header.decode_header(subject)))
                                        self.logger.info(f"メール件名: {decoded_subject}")
                                        
                                        # 件名パターンと一致するか確認
                                        if subject_pattern in decoded_subject:
                                            self.logger.info(f"該当するメールを発見: ID {email_id}, 件名: {decoded_subject}")
                                            
                                            # ファイル名が指定されている場合は本文も確認
                                            if file_stem:
                                                body = self._get_email_body(msg)
                                                if file_stem not in body:
                                                    self.logger.debug(f"メール本文にファイル名 '{file_stem}' が含まれていません")
                                                    self.processed_email_ids.add(email_id)
                                                    continue
                                            
                                            # URLを抽出
                                            self.logger.info("URL抽出処理を開始します...")
                                            download_url = self._extract_download_url(msg)
                                            if download_url:
                                                self.logger.info(f"ダウンロードURLを取得: {download_url}")
                                                self.processed_email_ids.add(email_id)
                                                return download_url
                                            else:
                                                self.logger.warning(f"メールからURLを抽出できませんでした")
                                                # デバッグ用：メール本文の一部を表示
                                                try:
                                                    body = self._get_email_body(msg)
                                                    self.logger.info(f"メール本文（最初の500文字）: {body[:500]}")
                                                except Exception as e:
                                                    self.logger.error(f"メール本文取得エラー: {e}")
                                    except Exception as decode_error:
                                        self.logger.warning(f"件名デコードエラー (ID {email_id}): {decode_error}")
                                
                                # 処理済みとして記録
                                self.processed_email_ids.add(email_id)
                            else:
                                self.logger.error(f"メール取得失敗 (ID {email_id}): {typ}")
                
                # 次のチェックまで待機
                remaining = (end_time - datetime.now(timezone.utc)).total_seconds()
                if remaining > check_interval:
                    self.logger.debug(f"次のチェックまで{check_interval}秒待機...")
                    time.sleep(check_interval)
                else:
                    time.sleep(max(1, remaining))
                    
            except Exception as e:
                self.logger.error(f"メール確認中にエラー: {e}")
                # エラー時は少し待ってリトライ
                time.sleep(check_interval)
        
        self.logger.warning(f"タイムアウト: {timeout}秒以内にメールが見つかりませんでした")
        return None
    
    def _get_email_date(self, msg: email.message.Message) -> Optional[datetime]:
        """メールの日時を取得"""
        try:
            date_str = msg.get('Date', '')
            if date_str:
                # email.utils.parsedate_to_datetimeを使用
                from email.utils import parsedate_to_datetime
                return parsedate_to_datetime(date_str)
        except Exception as e:
            self.logger.warning(f"日時解析エラー: {e}")
        return None
    
    def _get_email_body(self, msg: email.message.Message) -> str:
        """メール本文を取得"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = self._safe_decode_payload(payload)
                        if body:
                            break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = self._safe_decode_payload(payload)
        
        return body
    
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
            body = self._get_email_body(msg)
            
            if not body:
                self.logger.warning("メール本文を取得できませんでした")
                return None
            
            self.logger.info(f"メール本文の長さ: {len(body)}文字")
            
            # Word2XHTML5のダウンロードURLパターン
            # PDFファイルのURLを探す（改行やスペースを考慮）
            pdf_url_pattern = r'(http://trial\.nextpublishing\.jp/upload_46tate/do_download_pdf\?n=[^\s<>"{}|\\^`\[\]]+)'
            pdf_urls = re.findall(pdf_url_pattern, body, re.MULTILINE | re.DOTALL)
            
            self.logger.info(f"PDFパターンマッチ結果: {len(pdf_urls)}件")
            
            if pdf_urls:
                # 最初のPDF URLを返す
                self.logger.info(f"見つかったPDF URL: {pdf_urls[0]}")
                return pdf_urls[0]
            
            # ZIPファイルのURLも試す（ReVIEW変換の場合）
            zip_url_pattern = r'(https?://[^\s<>"{}|\\^`\[\]]+\.zip)'
            zip_urls = re.findall(zip_url_pattern, body)
            
            if zip_urls:
                return zip_urls[0]
            
            # より一般的なダウンロードURLパターン
            general_download_pattern = r'(https?://[^\s<>"{}|\\^`\[\]]+(?:download|dl|file)[^\s<>"{}|\\^`\[\]]+)'
            download_urls = re.findall(general_download_pattern, body, re.IGNORECASE)
            
            self.logger.info(f"一般的なダウンロードパターンマッチ結果: {len(download_urls)}件")
            
            if download_urls:
                self.logger.info(f"見つかったダウンロードURL: {download_urls[0]}")
                return download_urls[0]
            
            # すべてのHTTP/HTTPSのURLを探す（最後の手段）
            all_url_pattern = r'(https?://[^\s<>"{}|\\^`\[\]]+)'
            all_urls = re.findall(all_url_pattern, body)
            self.logger.info(f"すべてのURLパターンマッチ結果: {len(all_urls)}件")
            if all_urls:
                self.logger.info(f"見つかったURL（最初の3個）: {all_urls[:3]}")
            
            self.logger.warning("メール本文からダウンロードURLが見つかりませんでした")
            self.logger.info(f"メール本文（最初の1000文字）: {body[:1000]}")
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