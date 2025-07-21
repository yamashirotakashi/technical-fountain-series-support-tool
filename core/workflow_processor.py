"""ワークフロー処理管理モジュール"""
import os
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Callable
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from core.google_sheet import GoogleSheetClient
from core.file_manager import FileManager
from core.word_processor import WordProcessor
from utils.logger import get_logger
from utils.config import get_config


class WorkflowProcessor(QObject):
    """処理フロー全体を管理するクラス"""
    
    # シグナル定義
    log_message = pyqtSignal(str, str)  # message, level
    progress_updated = pyqtSignal(int)  # progress value
    status_updated = pyqtSignal(str)  # status message
    confirmation_needed = pyqtSignal(str, str, object)  # title, message, callback
    folder_selection_needed = pyqtSignal(object, str, object)  # repo_path, repo_name, default_folder
    file_paste_needed = pyqtSignal(list, str)  # processed_files, ncode
    
    def __init__(self, email_address: str = None, email_password: str = None):
        """
        WorkflowProcessorを初期化
        
        Args:
            email_address: メールアドレス（省略時は設定から取得）
            email_password: メールパスワード
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.config = get_config()
        
        # 各コンポーネントを初期化
        self.google_client = GoogleSheetClient()
        self.file_manager = FileManager()
        self.word_processor = WordProcessor()
        
        # WebClientとEmailMonitorは遅延初期化
        self._web_client = None
        self._email_monitor = None
        
        # メール設定（環境変数を優先）
        email_config = self.config.get_email_config()
        self.email_address = email_address or os.getenv('GMAIL_ADDRESS') or email_config.get('default_address')
        self.email_password = email_password or os.getenv('GMAIL_APP_PASSWORD')
        
        # ダイアログ結果の保存用
        self.dialog_result = None
    
    @property
    def web_client(self):
        """WebClientの遅延初期化"""
        if self._web_client is None:
            from core.web_client import WebClient
            self._web_client = WebClient()
        return self._web_client
    
    @property
    def email_monitor(self):
        """EmailMonitorの遅延初期化"""
        if self._email_monitor is None and self.email_password:
            from core.email_monitor import EmailMonitor
            self._email_monitor = EmailMonitor(self.email_address, self.email_password)
            self._email_monitor.connect()
        return self._email_monitor
    
    def process_n_codes(self, n_codes: List[str]):
        """
        複数のNコードを処理
        
        Args:
            n_codes: 処理するNコードのリスト
        """
        total = len(n_codes)
        self.emit_log(f"処理開始: {total}個のNコード", "INFO")
        
        for idx, n_code in enumerate(n_codes):
            self.emit_status(f"処理中: {n_code} ({idx + 1}/{total})")
            self.emit_progress(int((idx / total) * 100))
            
            try:
                self.process_single_n_code(n_code)
                self.emit_log(f"✓ {n_code} の処理が完了しました", "INFO")
            except Exception as e:
                self.emit_log(f"✗ {n_code} の処理に失敗: {str(e)}", "ERROR")
                self.logger.error(f"処理エラー {n_code}: {e}", exc_info=True)
        
        self.emit_progress(100)
        self.emit_status("すべての処理が完了しました")
        self.emit_log("処理完了", "INFO")
    
    def process_single_n_code(self, n_code: str):
        """
        単一のNコードを処理
        
        Args:
            n_code: 処理するNコード
        """
        self.logger.info(f"Nコード処理開始: {n_code}")
        
        # 1. Googleシートからリポジトリ名を取得
        self.emit_log(f"Googleシートから {n_code} を検索中...", "INFO")
        repo_info = self.google_client.search_n_code(n_code)
        
        if not repo_info:
            raise ValueError(f"Nコード {n_code} がGoogleシートに見つかりません")
        
        repo_name = repo_info['repository_name']
        self.emit_log(f"リポジトリ名: {repo_name}", "INFO")
        
        # 2. リポジトリフォルダを検索
        self.emit_log(f"リポジトリフォルダを検索中: {repo_name}", "INFO")
        repo_path = self.file_manager.find_repository_folder(repo_name)
        
        if not repo_path:
            raise ValueError(f"リポジトリフォルダが見つかりません: {repo_name}")
        
        # 3. 作業フォルダを特定
        self.emit_log("作業フォルダを検索中...", "INFO")
        
        # 保存された設定または自動検出された作業フォルダを取得
        default_work_folder = self.file_manager.find_work_folder_interactive(repo_path, repo_name)
        
        # フォルダ選択ダイアログを表示（シグナルを発行）
        self.selected_work_folder = None
        self.folder_selection_completed = False
        self.folder_selection_needed.emit(repo_path, repo_name, default_work_folder)
        
        # ダイアログの結果を待つ（最大30秒）
        timeout = 30
        start_time = time.time()
        while not self.folder_selection_completed and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            # GUIイベントループを処理するために必要
            from PyQt5.QtCore import QCoreApplication
            QCoreApplication.processEvents()
        
        work_folder = self.selected_work_folder
        
        if not work_folder:
            raise ValueError("作業フォルダが選択されませんでした")
        
        # 4. ZIPファイルを作成
        self.emit_log("ZIPファイルを作成中...", "INFO")
        zip_path = self.file_manager.create_zip(work_folder)
        
        # 5. ファイルをアップロード
        self.emit_log("ファイルをアップロード中...", "INFO")
        upload_success = self.web_client.upload_file(zip_path, self.email_address)
        
        if not upload_success:
            raise ValueError("ファイルのアップロードに失敗しました")
        
        # 6. メールを監視
        if self.email_password:
            self.emit_log("変換完了メールを待機中...", "INFO")
            
            # email_monitorプロパティを使用（遅延初期化）
            
            download_url = self.email_monitor.wait_for_email()
            
            if not download_url:
                raise ValueError("タイムアウト: メールが届きませんでした")
            
            # 7. ファイルをダウンロード
            self.emit_log("変換済みファイルをダウンロード中...", "INFO")
            download_path = self.file_manager.temp_dir / f"{n_code}_converted.zip"
            download_success = self.web_client.download_file(download_url, download_path)
            
            if not download_success:
                raise ValueError("ファイルのダウンロードに失敗しました")
            
            # 8. ZIPファイルを処理（展開 + 1行目削除）
            self.emit_log("ZIPファイルを処理中...", "INFO")
            processed_files = self.word_processor.process_zip_file(download_path)
            
            if not processed_files:
                raise ValueError("ZIPファイルの処理に失敗しました")
            
            self.emit_log(f"{len(processed_files)}個のWordファイルを処理しました", "INFO")
            
            # 9. Nフォルダと本文フォルダの存在確認
            ncode_folder = self.word_processor.find_ncode_folder(n_code)
            if not ncode_folder:
                raise ValueError(f"Nコードフォルダが見つかりません: {n_code}")
            
            honbun_folder = self.word_processor.find_honbun_folder(ncode_folder)
            if not honbun_folder:
                raise ValueError(f"本文フォルダの場所を特定できません: {ncode_folder}")
            
            # 10. ファイル情報を安全に収集
            self.emit_log("ファイル情報を収集中...", "INFO")
            file_info_list = []
            for file_path in processed_files:
                try:
                    if file_path.exists():
                        file_info = {
                            'name': file_path.name,
                            'path': str(file_path),
                            'size': file_path.stat().st_size
                        }
                    else:
                        file_info = {
                            'name': file_path.name,
                            'path': str(file_path),
                            'size': 0
                        }
                    file_info_list.append(file_info)
                except Exception as e:
                    self.emit_log(f"ファイル情報取得エラー {file_path.name}: {e}", "WARNING")
                    file_info = {
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': 0
                    }
                    file_info_list.append(file_info)
            
            # 11. ファイルペーストダイアログを表示
            self.emit_log("ファイル選択ダイアログを表示中...", "INFO")
            self.emit_log(f"処理済みファイル数: {len(file_info_list)}", "INFO")
            paste_result = self._show_file_paste_dialog(file_info_list, n_code)
            
            self.emit_log(f"ダイアログ結果: {paste_result}", "INFO")
            if not paste_result:
                raise ValueError("ユーザーによってキャンセルされました")
            
            self.emit_log(f"✓ {n_code} の処理が完了しました", "INFO")
        else:
            self.emit_log("メールパスワードが設定されていないため、手動でダウンロードしてください", "WARNING")
    
    def emit_log(self, message: str, level: str = "INFO"):
        """ログメッセージを送信"""
        # ログレベルを数値に変換
        import logging
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        numeric_level = level_map.get(level.upper(), logging.INFO)
        self.logger.log(numeric_level, message)
        self.log_message.emit(message, level)
    
    def emit_progress(self, value: int):
        """進捗を送信"""
        self.progress_updated.emit(value)
    
    def emit_status(self, message: str):
        """ステータスを送信"""
        self.status_updated.emit(message)
    
    def _show_file_paste_dialog(self, file_info_list: List[dict], ncode: str) -> bool:
        """
        ファイルペーストダイアログを表示（同期的に）
        
        Args:
            file_info_list: 処理済みファイル情報のリスト（辞書形式）
            ncode: 対象のNコード
        
        Returns:
            ダイアログが正常に完了した場合True
        """
        self.emit_log(f"_show_file_paste_dialog開始: {ncode}", "INFO")
        self.dialog_result = None
        
        # シグナルを発行してダイアログ表示を要求
        self.emit_log("file_paste_neededシグナルを発行中...", "INFO")
        self.file_paste_needed.emit(file_info_list, ncode)
        self.emit_log("file_paste_neededシグナルを発行しました", "INFO")
        
        # 結果を待機（UIスレッドで処理されるまで）
        timeout = 300  # 5分のタイムアウト
        start_time = time.time()
        wait_count = 0
        while self.dialog_result is None and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            wait_count += 1
            if wait_count % 50 == 0:  # 5秒ごとにログ出力
                self.emit_log(f"ダイアログ応答待機中... ({wait_count * 0.1:.1f}秒)", "INFO")
            # GUIイベントループを処理するために必要
            from PyQt5.QtCore import QCoreApplication
            QCoreApplication.processEvents()
        
        if self.dialog_result is None:
            self.emit_log("ファイルペーストダイアログがタイムアウトしました", "ERROR")
            return False
        
        self.emit_log(f"ダイアログ完了: completed={self.dialog_result}", "INFO")
        return self.dialog_result
    
    @pyqtSlot(bool)
    def on_file_paste_completed(self, success: bool):
        """ファイルペーストダイアログの結果を受信"""
        self.logger.info(f"ダイアログ結果受信: success={success}")
        self.dialog_result = success
    
    def _confirm_path(self, title: str, message: str) -> bool:
        """
        パス確認ダイアログを表示（同期的に）
        
        Args:
            title: ダイアログタイトル
            message: 確認メッセージ
        
        Returns:
            ユーザーが承認した場合True
        """
        # 簡易的な実装（実際のGUIでは適切なダイアログを使用）
        self.emit_log(f"確認: {message}", "INFO")
        return True  # デフォルトでTrueを返す
    
    def set_selected_work_folder(self, folder_path: str):
        """選択された作業フォルダを設定"""
        self.selected_work_folder = Path(folder_path) if folder_path else None
        self.folder_selection_completed = True
    
    def cleanup(self):
        """リソースをクリーンアップ"""
        if self._email_monitor:
            self._email_monitor.close()
        if self._web_client:
            self._web_client.close()
        self.file_manager.cleanup_temp_files()