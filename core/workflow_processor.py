"""ワークフロー処理管理モジュール"""
import os
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

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
    file_placement_confirmation_needed = pyqtSignal(str, list, object)  # honbun_folder_path, file_list, callback
    warning_dialog_needed = pyqtSignal(list, str)  # messages, result_type
    
    def __init__(self, email_address: str = None, email_password: str = None, process_mode: str = "traditional"):
        """
        WorkflowProcessorを初期化
        
        Args:
            email_address: メールアドレス（省略時は設定から取得）
            email_password: メールパスワード
            process_mode: 処理方式 ("traditional" または "api")
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.process_mode = process_mode
        
        # 初期化詳細ログ
        self.logger.info(f"[INIT] WorkflowProcessor初期化開始")
        self.logger.info(f"[INIT] process_mode: {process_mode}")
        self.logger.info(f"[INIT] email_address: {email_address}")
        self.logger.info(f"[INIT] has email_password: {email_password is not None}")
        
        # 各コンポーネントを初期化
        self.google_client = GoogleSheetClient()
        self.file_manager = FileManager()
        self.word_processor = WordProcessor()
        
        # WebClientとEmailMonitorは遅延初期化
        self._web_client = None
        self._email_monitor = None
        self._api_processor = None
        
        # 属性チェック
        self.logger.debug(f"[INIT] _api_processor初期化: {self._api_processor}")
        self.logger.debug(f"[INIT] hasattr(_api_processor): {hasattr(self, '_api_processor')}")
        self.logger.debug(f"[INIT] hasattr(api_processor): {hasattr(self, 'api_processor')}")
        
        # 全属性の確認
        self.logger.debug(f"[INIT] 全属性: {dir(self)}")
        
        # メール設定（環境変数を優先）
        email_config = self.config.get_email_config()
        self.email_address = email_address or os.getenv('GMAIL_ADDRESS') or email_config.get('default_address')
        self.email_password = email_password or os.getenv('GMAIL_APP_PASSWORD')
        
        # ダイアログ結果の保存用
        self.dialog_result = None
        self.file_placement_result = None
    
    @property
    def web_client(self):
        """WebClientの遅延初期化"""
        if self._web_client is None:
            from core.web_client import WebClient
            self._web_client = WebClient()
        return self._web_client
    
    @property
    def email_monitor(self):
        """EmailMonitorの遅延初期化（設定に基づく実装選択）"""
        if self._email_monitor is None:
            use_gmail_api = self.config.get('email', {}).get('use_gmail_api', False)
            
            if use_gmail_api:
                # Gmail API使用
                self.logger.info("Gmail APIを使用してメール監視を初期化します")
                from core.gmail_oauth_monitor import GmailOAuthMonitor
                credentials_path = self.config.get('email', {}).get('gmail_credentials_path', 'config/gmail_oauth_credentials.json')
                self._email_monitor = GmailOAuthMonitor(credentials_path)
                self._email_monitor.authenticate()
            else:
                # 従来のIMAP使用（パスワードが必要）
                if self.email_password:
                    self.logger.info("IMAPを使用してメール監視を初期化します")
                    from core.email_monitor import EmailMonitor
                    self._email_monitor = EmailMonitor(self.email_address, self.email_password)
                    self._email_monitor.connect()
                else:
                    self.logger.warning("メールパスワードが設定されていません")
                    return None
        return self._email_monitor
    
    @property
    def api_processor(self):
        """ApiProcessorの遅延初期化"""
        self.logger.debug(f"[PROPERTY] api_processorプロパティが呼ばれました")
        self.logger.debug(f"[PROPERTY] _api_processor現在の値: {self._api_processor}")
        
        if self._api_processor is None:
            self.logger.debug(f"[PROPERTY] ApiProcessorをインポート中...")
            from core.api_processor import ApiProcessor
            
            self.logger.debug(f"[PROPERTY] ApiProcessorをインスタンス化中...")
            self._api_processor = ApiProcessor()
            
            self.logger.debug(f"[PROPERTY] シグナルを接続中...")
            # シグナルを接続
            self._api_processor.log_message.connect(self.log_message.emit)
            self._api_processor.progress_updated.connect(self.progress_updated.emit)
            self._api_processor.warning_dialog_needed.connect(self.warning_dialog_needed.emit)
            
            self.logger.debug(f"[PROPERTY] ApiProcessor初期化完了: {self._api_processor}")
            
        return self._api_processor
    
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
            from PyQt6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
        
        work_folder = self.selected_work_folder
        
        if not work_folder:
            raise ValueError("作業フォルダが選択されませんでした")
        
        # 4. ZIPファイルを作成
        self.emit_log("ZIPファイルを作成中...", "INFO")
        zip_path = self.file_manager.create_zip(work_folder)
        
        # 5. 処理方式に応じて分岐
        self.logger.info(f"[PROCESS] 処理方式の分岐: process_mode={self.process_mode}")
        self.logger.info(f"[PROCESS] process_mode == 'api': {self.process_mode == 'api'}")
        self.logger.info(f"[PROCESS] process_mode type: {type(self.process_mode)}")
        self.logger.info(f"[PROCESS] process_mode repr: {repr(self.process_mode)}")
        
        if self.process_mode == "api":
            # API方式の処理
            self.emit_log("API方式で変換処理を開始...", "INFO")
            
            # エラートレース用の詳細ログ
            self.logger.debug(f"[API] api_processor取得前の属性チェック")
            self.logger.debug(f"[API] hasattr(self, '_api_processor'): {hasattr(self, '_api_processor')}")
            self.logger.debug(f"[API] hasattr(self, 'api_processor'): {hasattr(self, 'api_processor')}")
            self.logger.debug(f"[API] self._api_processor: {self._api_processor}")
            
            try:
                # APIで処理（プロパティを使用して遅延初期化）
                self.logger.debug(f"[API] api_processorプロパティにアクセス中...")
                api_proc = self.api_processor
                self.logger.debug(f"[API] api_processor取得成功: {api_proc}")
                
                self.logger.debug(f"[API] process_zip_fileを呼び出し中...")
                self.logger.debug(f"[API] ZIPファイルパス: {zip_path}")
                self.logger.debug(f"[API] ZIPファイルサイズ: {zip_path.stat().st_size:,} bytes")
                
                success, download_path, warnings = api_proc.process_zip_file(zip_path)
                
                self.logger.debug(f"[API] process_zip_file完了: success={success}, download_path={download_path}, warnings={len(warnings) if warnings else 0}")
                
                if warnings:
                    self.logger.debug(f"[API] 警告メッセージ:")
                    for i, warning in enumerate(warnings[:5]):  # 最初の5件
                        self.logger.debug(f"  {i+1}. {warning}")
                
            except AttributeError as e:
                self.logger.error(f"[API] AttributeError詳細: {e}")
                self.logger.error(f"[API] 利用可能な属性: {[attr for attr in dir(self) if not attr.startswith('_')]}")
                self.logger.error(f"[API] プライベート属性: {[attr for attr in dir(self) if attr.startswith('_') and not attr.startswith('__')]}")
                raise
            except Exception as e:
                self.logger.error(f"[API] 予期しないエラー: {type(e).__name__}: {e}")
                self.logger.error(f"[API] エラー詳細: {str(e)}")
                import traceback
                self.logger.error(f"[API] スタックトレース:\n{traceback.format_exc()}")
                raise
            
            if not success:
                # 失敗の場合、詳細なエラー情報を含める
                error_msg = "API変換処理が失敗しました"
                if warnings:
                    error_msg += f" (エラー/警告: {', '.join(warnings[:3])})"
                self.logger.error(f"[API] 処理失敗の詳細: {error_msg}")
                raise ValueError(error_msg)
            
            if not download_path:
                # ダウンロードファイルがない場合（エラーのみ）
                raise ValueError("変換ファイルのダウンロードに失敗しました")
            
            # 成功または一部成功の場合、処理を続行
            # download_pathは変換済みファイルのパス
            
        else:
            # 従来方式の処理
            self.emit_log("従来方式で処理を開始...", "INFO")
            
            # ファイルをアップロード
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
            else:
                self.emit_log("メールパスワードが設定されていないため、手動でダウンロードしてください", "WARNING")
                return
        
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
        
        # 10. 本文フォルダパス確認（要件2.6）
        self.emit_log("本文フォルダパス確認を表示中...", "INFO")
        selected_files = self._show_file_placement_confirmation(str(honbun_folder), processed_files)
        
        if not selected_files:
            raise ValueError("ユーザーによって処理がキャンセルされました")
        
        # 11. ファイル配置処理を実行
        self.emit_log(f"選択された{len(selected_files)}個のファイルを本文フォルダに配置中...", "INFO")
        copy_result = self._copy_files_to_honbun_folder(selected_files, honbun_folder)
        
        if not copy_result:
            raise ValueError("ファイル配置に失敗しました")
        
        self.emit_log(f"✓ {n_code} の処理が完了しました", "INFO")
    
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
    
    def _copy_files_to_honbun_folder(self, processed_files: List[Path], honbun_folder: Path) -> bool:
        """
        処理済みファイルを本文フォルダに配置
        
        Args:
            processed_files: 処理済みファイルのパスリスト
            honbun_folder: 配置先の本文フォルダ
        
        Returns:
            配置が成功した場合True
        """
        try:
            import shutil
            
            # 本文フォルダが存在しない場合は作成
            honbun_folder.mkdir(parents=True, exist_ok=True)
            self.emit_log(f"本文フォルダを確認/作成: {honbun_folder}", "INFO")
            
            success_count = 0
            for file_path in processed_files:
                try:
                    target_path = honbun_folder / file_path.name
                    shutil.copy2(file_path, target_path)
                    success_count += 1
                    self.emit_log(f"ファイルコピー完了: {file_path.name}", "INFO")
                except Exception as e:
                    self.emit_log(f"ファイルコピーエラー {file_path.name}: {e}", "ERROR")
            
            self.emit_log(f"ファイル配置完了: {success_count}/{len(processed_files)} ファイル", "INFO")
            return success_count > 0
            
        except Exception as e:
            self.emit_log(f"ファイル配置処理エラー: {e}", "ERROR")
            return False
    
    def _show_file_placement_confirmation(self, honbun_folder_path: str, file_list: List[Path]) -> List[Path]:
        """
        ファイル配置確認ダイアログを表示（同期的に）
        
        Args:
            honbun_folder_path: 本文フォルダのパス
            file_list: 処理済みファイルのリスト
        
        Returns:
            選択されたファイルのリスト（キャンセルの場合は空リスト）
        """
        import time
        
        self.file_placement_result = None
        
        # シグナルを発行して確認ダイアログ表示を要求
        self.file_placement_confirmation_needed.emit(honbun_folder_path, file_list, self.on_file_placement_confirmed)
        
        # 結果を待機（UIスレッドで処理されるまで）
        timeout = 60  # 1分のタイムアウト
        start_time = time.time()
        while self.file_placement_result is None and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            # GUIイベントループを処理するために必要
            from PyQt6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
        
        if self.file_placement_result is None:
            self.emit_log("ファイル配置確認がタイムアウトしました", "ERROR")
            return []
        
        return self.file_placement_result if self.file_placement_result else []
    
    def on_file_placement_confirmed(self, selected_files: List[Path]):
        """ファイル配置確認の結果を受信"""
        print(f"[DEBUG] WorkflowProcessor.on_file_placement_confirmed: 受信したファイル数: {len(selected_files)}")
        self.file_placement_result = selected_files
        self.emit_log(f"ファイル配置確認結果: {len(selected_files)}個のファイルを選択", "INFO")
    
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