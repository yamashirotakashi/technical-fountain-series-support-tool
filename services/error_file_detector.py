"""エラーファイル検知サービスモジュール"""
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from pathlib import Path
from typing import List, Dict, Optional
import logging
import time
import re

from services.nextpublishing_service import NextPublishingService, UploadSettings
from core.email_monitor_enhanced import EmailMonitorEnhanced
from utils.config import get_config


class ErrorFileDetectorWorker(QThread):
    """エラーファイル検知用ワーカースレッド"""
    
    # シグナル定義
    progress_updated = pyqtSignal(int, int)  # 現在, 全体
    log_message = pyqtSignal(str, str)  # メッセージ, レベル
    status_updated = pyqtSignal(str)  # ステータステキスト
    file_processed = pyqtSignal(str, bool, str)  # ファイル名, 成功/失敗, メッセージ
    detection_completed = pyqtSignal(list)  # エラーファイルリスト
    
    def __init__(self, n_codes: List[str], email_password: Optional[str] = None):
        """
        初期化
        
        Args:
            n_codes: 処理するNコードのリスト
            email_password: メールパスワード（メール監視を使う場合）
        """
        super().__init__()
        self.n_codes = n_codes
        self.email_password = email_password
        self.logger = logging.getLogger(__name__)
        self._is_running = True
        self.config = get_config()
        
    def run(self):
        """エラー検知処理を実行"""
        email_monitor = None
        try:
            self.log_message.emit("エラーファイル検知を開始します", "INFO")
            self.status_updated.emit("初期化中...")
            
            # 1. Nコードから既存のWordファイルを取得
            word_files = self._get_word_files_from_ncodes()
            if not word_files:
                self.log_message.emit("処理対象のWordファイルが見つかりません", "ERROR")
                return
            
            self.log_message.emit(f"{len(word_files)}個のWordファイルを検査します", "INFO")
            
            # 2. NextPublishingサービスを初期化
            service = NextPublishingService()
            
            # 3. メール監視を初期化（パスワードが提供されている場合）
            email_monitor = None
            if self.email_password:
                try:
                    email_monitor = EmailMonitorEnhanced(
                        email_address=UploadSettings().email,
                        password=self.email_password
                    )
                    email_monitor.connect()
                    email_monitor.start_monitoring()  # アップロード前に監視開始
                    self.log_message.emit("メール監視を有効化しました", "INFO")
                except Exception as e:
                    self.log_message.emit(f"メール監視の初期化に失敗: {e}", "WARNING")
            
            # 4. ファイルを処理
            error_files = []
            total_files = len(word_files)
            
            # バッチサイズを決定（10ファイルずつ）
            batch_size = 10
            
            for i in range(0, total_files, batch_size):
                if not self._is_running:
                    break
                
                batch = word_files[i:i + batch_size]
                batch_num = i // batch_size + 1
                self.status_updated.emit(f"バッチ {batch_num} を処理中...")
                
                # バッチアップロード
                results = service.upload_multiple_files(batch, batch_size)
                
                # アップロード結果を記録
                for result in results:
                    if result['success']:
                        self.log_message.emit(
                            f"アップロード成功: {result['file_path'].name}",
                            "INFO"
                        )
                    else:
                        self.log_message.emit(
                            f"アップロード失敗: {result['file_path'].name} - {result['message']}",
                            "ERROR"
                        )
                
                # メール到着を待機
                if email_monitor and all(r['success'] for r in results):
                    self.status_updated.emit("変換メールを待機中...")
                    self.log_message.emit(f"バッチ {batch_num} の変換メールを待機中（最大20分）", "INFO")
                    
                    # 各ファイルのメールを待機
                    for j, file_path in enumerate(batch):
                        if not self._is_running:
                            break
                        
                        # 進捗更新
                        current_file_index = i + j
                        self.progress_updated.emit(current_file_index + 1, total_files)
                        
                        # メール待機とPDFチェック
                        is_error = self._check_file_conversion(
                            file_path,
                            email_monitor,
                            service
                        )
                        
                        if is_error:
                            error_files.append(file_path)
                            self.file_processed.emit(
                                file_path.name,
                                False,
                                "PDF生成エラー"
                            )
                        else:
                            self.file_processed.emit(
                                file_path.name,
                                True,
                                "正常"
                            )
                else:
                    # メール監視なしの場合は手動確認を促す
                    self.log_message.emit(
                        "メール監視が無効です。手動でメールを確認してください",
                        "WARNING"
                    )
                    # 仮の進捗更新
                    self.progress_updated.emit(i + len(batch), total_files)
            
            # 5. 結果を通知
            self.status_updated.emit("検査完了")
            if error_files:
                self.log_message.emit(
                    f"エラーファイル検出: {len(error_files)}個",
                    "WARNING"
                )
                for ef in error_files:
                    self.log_message.emit(f"  - {ef.name}", "ERROR")
            else:
                self.log_message.emit("エラーファイルは検出されませんでした", "INFO")
            
            # 完了シグナル
            self.detection_completed.emit(error_files)
            
        except Exception as e:
            self.logger.error(f"エラー検知処理でエラー: {e}", exc_info=True)
            self.log_message.emit(f"エラーが発生しました: {str(e)}", "ERROR")
        finally:
            if 'service' in locals():
                service.close()
            if email_monitor:
                email_monitor.close()
    
    def _get_word_files_from_ncodes(self) -> List[Path]:
        """Nコードから既存のWordファイルを取得"""
        word_files = []
        
        # 出力ベースディレクトリを取得
        output_base = Path(self.config.get('paths.output_base', 'G:\\.shortcut-targets-by-id\\0B6euJ_grVeOeMnJLU1IyUWgxeWM\\NP-IRD'))
        
        for n_code in self.n_codes:
            # Nフォルダのパスを構築
            n_folder = output_base / n_code
            
            if n_folder.exists() and n_folder.is_dir():
                # Wordファイルを検索
                docx_files = list(n_folder.glob("*.docx"))
                if docx_files:
                    word_files.extend(docx_files)
                    self.log_message.emit(
                        f"{n_code}: {len(docx_files)}個のWordファイルを発見",
                        "INFO"
                    )
                else:
                    self.log_message.emit(
                        f"{n_code}: Wordファイルが見つかりません",
                        "WARNING"
                    )
            else:
                self.log_message.emit(
                    f"{n_code}: フォルダが存在しません",
                    "WARNING"
                )
        
        return word_files
    
    def _check_file_conversion(
        self,
        file_path: Path,
        email_monitor: EmailMonitorEnhanced,
        service: NextPublishingService
    ) -> bool:
        """
        ファイルの変換結果をチェック
        
        Returns:
            True: エラーファイル, False: 正常ファイル
        """
        try:
            if not self._is_running:
                return False
            
            # メールを待機してURLを取得
            from utils.constants import EMAIL_SENDERS, EMAIL_SUBJECTS, EMAIL_TIMEOUTS
            pdf_url = email_monitor.wait_for_email(
                subject_pattern=EMAIL_SUBJECTS['WORD2XHTML5'],
                from_address=EMAIL_SENDERS['WORD2XHTML5'],
                timeout=EMAIL_TIMEOUTS['WORD2XHTML5'],
                check_interval=30,
                file_stem=file_path.stem
            )
            
            if pdf_url:
                # PDFダウンロード可否をチェック
                is_downloadable, message = service.check_pdf_downloadable(pdf_url)
                if not is_downloadable:
                    self.log_message.emit(
                        f"PDFダウンロードエラー: {file_path.name} - {message}",
                        "ERROR"
                    )
                return not is_downloadable  # ダウンロード不可 = エラー
            else:
                # メールが見つからない = エラー扱い
                self.log_message.emit(
                    f"メール待機タイムアウト: {file_path.name}",
                    "WARNING"
                )
                return True
            
        except Exception as e:
            self.logger.error(f"ファイルチェックエラー: {e}")
            return True  # エラー = エラー扱い
    
    def _extract_pdf_url(self, email_content: str) -> Optional[str]:
        """メール本文からPDFダウンロードURLを抽出"""
        # PDFファイルのURLパターン
        pattern = r'(http://trial\.nextpublishing\.jp/upload_46tate/do_download_pdf\?[^\s]+)'
        match = re.search(pattern, email_content)
        return match.group(1) if match else None
    
    def stop(self):
        """処理を停止"""
        self._is_running = False