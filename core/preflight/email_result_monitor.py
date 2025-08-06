"""Pre-flight Check結果メール監視モジュール"""
from __future__ import annotations

import re
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import email

from core.email_monitor import EmailMonitor
from utils.logger import get_logger

# ConfigManagerのインポート（try-except ImportErrorパターン）
try:
    from .config_manager import ConfigManager
except ImportError:
    ConfigManager = None


class PreflightEmailResultMonitor(EmailMonitor):
    """Pre-flight Check用のメール監視クラス"""
    
    def __init__(self, email_address: str, password: str, config_manager: Optional['ConfigManager'] = None):
        super().__init__(email_address, password)
        self.logger = get_logger(__name__)
        self.config_manager = config_manager
        
    def wait_for_results(self, job_ids: List[str], timeout: Optional[int] = None, 
                        check_interval: Optional[int] = None) -> Dict[str, Tuple[str, Optional[str]]]:
        """
        複数のジョブ結果メールを待機
        
        Args:
            job_ids: 監視対象のジョブIDリスト
            timeout: 全体のタイムアウト時間（秒）
            check_interval: チェック間隔（秒）
            
        Returns:
            {job_id: (status, error_message)} の辞書
            status: "success", "error", "timeout"
        """
        # ConfigManagerから設定値を取得（デフォルト値付き）
        if timeout is None:
            timeout = self.config_manager.get("email.result_monitor.timeout", 2400) if self.config_manager else 2400
        if check_interval is None:
            check_interval = self.config_manager.get("email.result_monitor.check_interval", 30) if self.config_manager else 30
            
        if not self.connection:
            self.connect()
            
        results = {}
        pending_jobs = set(job_ids)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=timeout)
        
        self.logger.info(f"メール結果待機開始: {len(job_ids)}個のジョブ (タイムアウト: {timeout}秒)")
        
        while datetime.now() < end_time and pending_jobs:
            try:
                # 新しいメールを検索
                since_date = start_time.strftime("%d-%b-%Y")
                
                # Word2XHTML5からのメールを検索
                search_patterns = [
                    "Word2XHTML5",
                    "変換完了",
                    "変換エラー",
                    "処理完了",
                    "nextpublishing"
                ]
                
                # 日付以降のすべてのメールを取得
                search_criteria = f'SINCE "{since_date}"'
                typ, data = self.connection.search(None, search_criteria)
                
                if typ == 'OK':
                    email_ids = data[0].split()
                    
                    if email_ids:
                        # 新しいメールから順に確認
                        for email_id in reversed(email_ids):
                            if not pending_jobs:
                                break
                                
                            # メールを取得
                            typ, msg_data = self.connection.fetch(email_id, '(RFC822)')
                            
                            if typ == 'OK':
                                # メールを解析
                                raw_email = msg_data[0][1]
                                msg = email.message_from_bytes(raw_email)
                                
                                # 件名と本文を確認
                                result = self._check_email_for_job(msg, list(pending_jobs))
                                
                                if result:
                                    job_id, status, error_msg = result
                                    results[job_id] = (status, error_msg)
                                    pending_jobs.discard(job_id)
                                    
                                    self.logger.info(
                                        f"ジョブ結果取得: {job_id} - {status}"
                                        f"{f' ({error_msg})' if error_msg else ''}"
                                    )
                
                # 進捗ログ
                completed = len(results)
                total = len(job_ids)
                self.logger.info(f"進捗: {completed}/{total} ジョブ完了")
                
                # 次のチェックまで待機
                if pending_jobs:
                    remaining = (end_time - datetime.now()).total_seconds()
                    if remaining > check_interval:
                        self.logger.info(f"次のチェックまで{check_interval}秒待機...")
                        time.sleep(check_interval)
                    else:
                        time.sleep(max(1, remaining))
                        
            except Exception as e:
                self.logger.error(f"メール確認中にエラー: {e}")
                time.sleep(check_interval)
        
        # タイムアウトしたジョブを記録
        for job_id in pending_jobs:
            results[job_id] = ("timeout", "結果メールがタイムアウトしました")
            self.logger.warning(f"ジョブタイムアウト: {job_id}")
            
        return results
        
    def _check_email_for_job(self, msg: email.message.Message, 
                           job_ids: List[str]) -> Optional[Tuple[str, str, Optional[str]]]:
        """
        メールが特定のジョブに関連するか確認
        
        Args:
            msg: メールメッセージ
            job_ids: チェック対象のジョブIDリスト
            
        Returns:
            (job_id, status, error_message) のタプル、または None
        """
        try:
            # 件名を取得
            subject = msg.get('Subject', '')
            if subject:
                decoded_subject = str(email.header.make_header(
                    email.header.decode_header(subject)
                ))
            else:
                decoded_subject = ""
                
            # 本文を取得
            body = self._extract_body(msg)
            
            # 全体のテキストから判定
            full_text = f"{decoded_subject}\n{body}"
            
            # ジョブIDを探す
            for job_id in job_ids:
                if job_id in full_text:
                    # 成功/失敗を判定
                    status, error_msg = self._determine_result_status(full_text)
                    return (job_id, status, error_msg)
                    
            # ファイル名ベースでの照合も試みる
            # job_id形式: "job_1234567890_filename"
            for job_id in job_ids:
                parts = job_id.split('_', 2)
                if len(parts) >= 3:
                    filename = parts[2]
                    if filename in full_text:
                        status, error_msg = self._determine_result_status(full_text)
                        return (job_id, status, error_msg)
                        
        except Exception as e:
            self.logger.error(f"メール解析エラー: {e}")
            
        return None
        
    def _extract_body(self, msg: email.message.Message) -> str:
        """メール本文を抽出（親クラスのメソッドを活用）"""
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
        
    def _determine_result_status(self, text: str) -> Tuple[str, Optional[str]]:
        """
        メールテキストから成功/失敗を判定
        
        Args:
            text: メールの全テキスト
            
        Returns:
            (status, error_message) のタプル
        """
        text_lower = text.lower()
        
        # エラーパターン
        error_patterns = [
            (r'エラー', 'PDF変換エラー'),
            (r'失敗', 'PDF変換失敗'),
            (r'error', 'Conversion error'),
            (r'failed', 'Conversion failed'),
            (r'変換できません', 'PDF変換不可'),
            (r'処理できません', '処理不可'),
            (r'対応していません', '非対応フォーマット'),
        ]
        
        for pattern, message in error_patterns:
            if re.search(pattern, text_lower):
                # より詳細なエラーメッセージを抽出
                detailed_error = self._extract_error_details(text)
                return ("error", detailed_error or message)
                
        # 成功パターン
        success_patterns = [
            r'完了',
            r'成功',
            r'ダウンロード',
            r'download',
            r'completed',
            r'success',
            r'\.pdf',
            r'\.zip'
        ]
        
        for pattern in success_patterns:
            if re.search(pattern, text_lower):
                return ("success", None)
                
        # 判定できない場合はエラー扱い
        return ("error", "結果判定不能")
        
    def _extract_error_details(self, text: str) -> Optional[str]:
        """エラーの詳細を抽出"""
        # エラー詳細のパターン
        detail_patterns = [
            r'エラー[：:]\s*(.+?)[\n。]',
            r'理由[：:]\s*(.+?)[\n。]',
            r'原因[：:]\s*(.+?)[\n。]',
            r'Error[：:]\s*(.+?)[\n\.]',
            r'Reason[：:]\s*(.+?)[\n\.]',
        ]
        
        for pattern in detail_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
                
        return None