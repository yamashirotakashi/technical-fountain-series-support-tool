"""強化版IMAP結果監視モジュール"""
from __future__ import annotations

import re
import time
import email
import imaplib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from email.header import decode_header
from email.utils import parsedate_to_datetime

from .email_result_monitor import PreflightEmailResultMonitor
from utils.logger import get_logger

# ConfigManagerをインポート
try:
    from src.slack_pdf_poster import ConfigManager
except ImportError:
    ConfigManager = None


@dataclass
class EmailSearchResult:
    """メール検索結果"""
    message_id: str
    subject: str
    sender: str
    received_time: datetime
    job_id: Optional[str]
    download_links: List[str]
    body_text: str
    is_success: bool
    is_error: bool
    
    
class EnhancedEmailMonitor(PreflightEmailResultMonitor):
    """セキュリティ強化版のメール監視クラス"""
    
    # 監視対象の送信元アドレス（ホワイトリスト）
    TRUSTED_SENDERS = {
        'nextpublishing.jp',
        'trial.nextpublishing.jp',
        'epub.nextpublishing.jp'
    }
    
    # 件名パターン（正規表現）
    SUBJECT_PATTERNS = {
        'success': [
            r'.*変換.*完了.*',
            r'.*処理.*完了.*',  
            r'.*conversion.*complete.*',
            r'.*job.*complete.*',
            r'.*受付番号.*',
        ],
        'error': [
            r'.*エラー.*',
            r'.*失敗.*',
            r'.*error.*',
            r'.*failed.*',
            r'.*問題.*',
        ]
    }
    
    # ダウンロードリンクパターン
    DOWNLOAD_LINK_PATTERNS = [
        r'https?://[^\s]+\.(?:docx?|pdf|zip)',
        r'https?://trial\.nextpublishing\.jp/[^\s]+',
        r'https?://[^\s]+/download[^\s]*',
    ]
    
    def __init__(self, gmail_address: str, gmail_password: str, config_manager: Optional['ConfigManager'] = None):
        super().__init__(gmail_address, gmail_password)
        self.logger = get_logger(__name__)
        self.config_manager = config_manager or (ConfigManager() if ConfigManager else None)
        self._processed_message_ids: Set[str] = set()
        
    def _is_trusted_sender(self, sender_email: str) -> bool:
        """送信者が信頼できるかどうかをチェック
        
        Args:
            sender_email: 送信者のメールアドレス
            
        Returns:
            信頼できる送信者の場合True
        """
        if not sender_email:
            return False
            
        sender_email = sender_email.lower()
        
        for trusted_domain in self.TRUSTED_SENDERS:
            if trusted_domain in sender_email:
                return True
                
        return False
    
    def _extract_job_id_enhanced(self, subject: str, body: str) -> Optional[str]:
        """件名と本文からジョブIDを抽出（強化版）
        
        Args:
            subject: メール件名
            body: メール本文
            
        Returns:
            抽出されたジョブID
        """
        # 複数のパターンでジョブIDを検索
        patterns = [
            # 日本語パターン
            r'受付番号[:：]\s*([A-Za-z0-9\-_]+)',
            r'処理ID[:：]\s*([A-Za-z0-9\-_]+)',
            r'ジョブID[:：]\s*([A-Za-z0-9\-_]+)',
            r'整理番号[:：]\s*([A-Za-z0-9\-_]+)',
            
            # 英語パターン
            r'Job\s*ID[:：]\s*([A-Za-z0-9\-_]+)',
            r'Reference[:：]\s*([A-Za-z0-9\-_]+)',
            r'Ticket[:：]\s*([A-Za-z0-9\-_]+)',
            
            # URL内のパターン
            r'/job/([A-Za-z0-9\-_]+)',
            r'job_id=([A-Za-z0-9\-_]+)',
            
            # タイムスタンプベースのパターン
            r'(\d{10,13}_[A-Za-z0-9\-_]+)',
        ]
        
        # 件名から検索
        for pattern in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                job_id = match.group(1)
                self.logger.debug(f"件名からジョブID抽出: {job_id}")
                return job_id
        
        # 本文から検索
        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                job_id = match.group(1)
                self.logger.debug(f"本文からジョブID抽出: {job_id}")
                return job_id
        
        return None
    
    def _extract_download_links(self, body: str) -> List[str]:
        """本文からダウンロードリンクを抽出
        
        Args:
            body: メール本文
            
        Returns:
            ダウンロードリンクのリスト
        """
        links = []
        
        for pattern in self.DOWNLOAD_LINK_PATTERNS:
            matches = re.findall(pattern, body, re.IGNORECASE)
            links.extend(matches)
        
        # 重複を削除し、信頼できるドメインのみフィルタリング
        unique_links = []
        for link in set(links):
            for trusted_domain in self.TRUSTED_SENDERS:
                if trusted_domain in link:
                    unique_links.append(link)
                    break
        
        return unique_links
    
    def _classify_email_type(self, subject: str, body: str) -> Tuple[bool, bool]:
        """メールタイプを分類（成功/エラー）
        
        Args:
            subject: メール件名
            body: メール本文
            
        Returns:
            (is_success, is_error)のタプル
        """
        content = f"{subject} {body}".lower()
        
        # エラーパターンのチェック
        is_error = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.SUBJECT_PATTERNS['error']
        )
        
        # 成功パターンのチェック
        is_success = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.SUBJECT_PATTERNS['success']
        )
        
        return is_success, is_error
    
    def search_results_enhanced(
        self,
        job_ids: List[str],
        search_hours: Optional[int] = None,
        max_wait_minutes: Optional[int] = None
    ) -> Dict[str, EmailSearchResult]:
        """強化版の結果検索
        
        Args:
            job_ids: 検索対象のジョブIDリスト
            search_hours: 検索範囲（時間）
            max_wait_minutes: 最大待機時間（分）
            
        Returns:
            ジョブID -> 検索結果の辞書
        """
        # ConfigManagerから設定値を取得（デフォルト値付き）
        if search_hours is None:
            search_hours = self.config_manager.get("email.search_hours", 24) if self.config_manager else 24
        if max_wait_minutes is None:
            max_wait_minutes = self.config_manager.get("email.max_wait_minutes", 20) if self.config_manager else 20
        
        results = {}
        found_job_ids = set()
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        self.logger.info(f"強化版結果検索開始: {len(job_ids)}件のジョブID")
        self.logger.info(f"検索範囲: {search_hours}時間, 最大待機: {max_wait_minutes}分")
        
        try:
            # IMAP接続
            self.connect()
            
            # 検索用の日付範囲を設定
            since_date = datetime.now() - timedelta(hours=search_hours)
            since_str = since_date.strftime("%d-%b-%Y")
            
            while len(found_job_ids) < len(job_ids):
                elapsed_minutes = (time.time() - start_time) / 60
                
                if elapsed_minutes >= max_wait_minutes:
                    self.logger.warning(f"最大待機時間に達しました: {max_wait_minutes}分")
                    break
                
                # 信頼できる送信者からのメールを検索
                search_criteria = []
                for sender_domain in self.TRUSTED_SENDERS:
                    search_criteria.append(f'(FROM "{sender_domain}")')
                
                search_query = f'(SINCE {since_str}) (OR {" ".join(search_criteria)})'
                
                self.logger.debug(f"IMAP検索クエリ: {search_query}")
                
                # メール検索実行
                _, message_ids = self.mail.search(None, search_query)
                
                if not message_ids[0]:
                    self.logger.debug("該当するメールが見つかりません")
                    # ConfigManagerから待機時間を取得
                    wait_time = self.config_manager.get("email.search_retry_interval", 30) if self.config_manager else 30
                    time.sleep(wait_time)  # ConfigManagerから取得した秒数で待機して再検索
                    continue
                
                # メッセージIDを処理
                for msg_id in message_ids[0].split():
                    msg_id_str = msg_id.decode()
                    
                    # 既に処理済みのメッセージはスキップ
                    if msg_id_str in self._processed_message_ids:
                        continue
                    
                    try:
                        # メール取得
                        _, msg_data = self.mail.fetch(msg_id, '(RFC822)')
                        email_msg = email.message_from_bytes(msg_data[0][1])
                        
                        # 送信者チェック
                        sender = email_msg.get('From', '')
                        if not self._is_trusted_sender(sender):
                            self.logger.debug(f"信頼できない送信者をスキップ: {sender}")
                            continue
                        
                        # 件名デコード
                        subject_raw = email_msg.get('Subject', '')
                        subject = self._decode_header(subject_raw)
                        
                        # 本文取得
                        body = self._get_email_body(email_msg)
                        
                        # ジョブID抽出
                        extracted_job_id = self._extract_job_id_enhanced(subject, body)
                        
                        if extracted_job_id and extracted_job_id in job_ids:
                            # 受信時刻取得
                            date_header = email_msg.get('Date')
                            received_time = parsedate_to_datetime(date_header) if date_header else datetime.now()
                            
                            # ダウンロードリンク抽出
                            download_links = self._extract_download_links(body)
                            
                            # メールタイプ分類
                            is_success, is_error = self._classify_email_type(subject, body)
                            
                            # 結果作成
                            result = EmailSearchResult(
                                message_id=msg_id_str,
                                subject=subject,
                                sender=sender,
                                received_time=received_time,
                                job_id=extracted_job_id,
                                download_links=download_links,
                                body_text=body[:1000],  # 最初の1000文字のみ
                                is_success=is_success,
                                is_error=is_error
                            )
                            
                            results[extracted_job_id] = result
                            found_job_ids.add(extracted_job_id)
                            
                            self.logger.info(
                                f"結果メール発見: {extracted_job_id} - "
                                f"{'成功' if is_success else 'エラー' if is_error else '不明'}"
                            )
                        
                        # 処理済みとしてマーク
                        self._processed_message_ids.add(msg_id_str)
                        
                    except Exception as e:
                        self.logger.error(f"メール処理エラー: {msg_id_str} - {e}")
                        continue
                
                # 全て見つかった場合は終了
                if len(found_job_ids) >= len(job_ids):
                    self.logger.info("全てのジョブIDの結果が見つかりました")
                    break
                
                # まだ見つからないジョブIDがある場合は待機
                remaining_jobs = set(job_ids) - found_job_ids
                self.logger.info(
                    f"待機中... 残り{len(remaining_jobs)}件: {list(remaining_jobs)[:3]}..."
                )
                # ConfigManagerから待機時間を取得
                wait_time = self.config_manager.get("email.polling_interval", 60) if self.config_manager else 60
                time.sleep(wait_time)  # ConfigManagerから取得した秒数で待機
                
        except Exception as e:
            self.logger.error(f"強化版検索エラー: {e}", exc_info=True)
        
        finally:
            self.disconnect()
        
        # 見つからなかったジョブIDの結果も作成
        for job_id in job_ids:
            if job_id not in results:
                results[job_id] = EmailSearchResult(
                    message_id="",
                    subject="",
                    sender="",
                    received_time=datetime.now(),
                    job_id=job_id,
                    download_links=[],
                    body_text="",
                    is_success=False,
                    is_error=False
                )
        
        self.logger.info(f"強化版検索完了: {len(found_job_ids)}/{len(job_ids)}件発見")
        return results
    
    def disconnect(self) -> None:
        """IMAP接続を切断"""
        try:
            self.close()  # 親クラスのcloseメソッドを呼び出し
        except Exception as e:
            self.logger.warning(f"メール接続切断時の警告: {e}")
    
    def cleanup(self) -> None:
        """リソースのクリーンアップ（別名メソッド）"""
        self.disconnect()
    
    def get_search_statistics(self, results: Dict[str, EmailSearchResult]) -> Dict[str, any]:
        """検索結果の統計情報を取得
        
        Args:
            results: search_results_enhancedの結果
            
        Returns:
            統計情報の辞書
        """
        total_jobs = len(results)
        found_jobs = len([r for r in results.values() if r.message_id])
        success_jobs = len([r for r in results.values() if r.is_success])
        error_jobs = len([r for r in results.values() if r.is_error])
        
        download_links_count = sum(len(r.download_links) for r in results.values())
        
        return {
            'total_jobs': total_jobs,
            'found_count': found_jobs,
            'not_found_count': total_jobs - found_jobs,
            'success_count': success_jobs,
            'error_count': error_jobs,
            'unknown_count': total_jobs - success_jobs - error_jobs,
            'download_links_total': download_links_count,
            'success_rate': round(success_jobs / total_jobs * 100, 1) if total_jobs > 0 else 0,
            'found_rate': round(found_jobs / total_jobs * 100, 1) if total_jobs > 0 else 0
        }