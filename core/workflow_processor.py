from __future__ import annotations
"""ワークフロー処理管理モジュール"""
import os
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from core.google_sheet import GoogleSheetClient
from core.file_manager import FileManager
from core.word_processor import WordProcessor
from utils.logger import get_logger
from utils.config import get_config


class WorkflowProcessor(QObject):
    """
    処理フロー全体を管理するクラス（リファクタリング済み）
    
    このクラスは新しい3クラス構成のファサードとして機能し、
    既存のAPIインターフェースを維持しながら内部は分離されたアーキテクチャを使用します。
    """
    
    # シグナル定義（既存インターフェース維持）
    log_message = pyqtSignal(str, str)  # message, level
    progress_updated = pyqtSignal(int)  # progress value
    status_updated = pyqtSignal(str)  # status message
    confirmation_needed = pyqtSignal(str, str, object)  # title, message, callback
    folder_selection_needed = pyqtSignal(object, str, object)  # repo_path, repo_name, default_folder
    file_placement_confirmation_needed = pyqtSignal(str, list, object)  # honbun_folder_path, file_list, callback
    warning_dialog_needed = pyqtSignal(list, str)  # messages, result_type
    
    def __init__(self, email_address: str = None, email_password: str = None, process_mode: str = "traditional"):
        """
        WorkflowProcessorを初期化（新アーキテクチャ使用）
        
        Args:
            email_address: メールアドレス（省略時は設定から取得）
            email_password: メールパスワード
            process_mode: 処理方式 ("traditional", "api", "gmail_api")
        """
        super().__init__()
        self.logger = get_logger(__name__)
        
        # 初期化詳細ログ
        self.logger.info(f"[INIT] WorkflowProcessor初期化開始（リファクタリング版）")
        self.logger.info(f"[INIT] process_mode: {process_mode}")
        self.logger.info(f"[INIT] email_address: {email_address}")
        self.logger.info(f"[INIT] has email_password: {email_password is not None}")
        
        # 新しい3層アーキテクチャの初期化
        self.config_manager = ConfigurationManager(email_address, email_password, process_mode)
        self.processing_engine = ProcessingEngine(self.config_manager)
        self.orchestrator = WorkflowOrchestrator(self.config_manager, self.processing_engine)
        
        # シグナルを接続（既存インターフェース維持）
        self._connect_signals()
        
        # レガシー互換性のための属性
        self._setup_legacy_compatibility()
        
        self.logger.info(f"[INIT] WorkflowProcessor初期化完了（新アーキテクチャ）")
    
    def _connect_signals(self):
        """オーケストレーターからのシグナルを転送"""
        self.orchestrator.log_message.connect(self.log_message.emit)
        self.orchestrator.progress_updated.connect(self.progress_updated.emit)
        self.orchestrator.status_updated.connect(self.status_updated.emit)
        self.orchestrator.confirmation_needed.connect(self.confirmation_needed.emit)
        self.orchestrator.folder_selection_needed.connect(self.folder_selection_needed.emit)
        self.orchestrator.file_placement_confirmation_needed.connect(self.file_placement_confirmation_needed.emit)
        self.orchestrator.warning_dialog_needed.connect(self.warning_dialog_needed.emit)
    
    def _setup_legacy_compatibility(self):
        """レガシーコードとの互換性のための属性設定"""
        # 既存コードで参照される可能性のある属性
        self.config = self.config_manager.config
        self.process_mode = self.config_manager.process_mode
        self.email_address = self.config_manager.email_address
        self.email_password = self.config_manager.email_password
        
        # ダイアログ結果保存用（既存インターフェース）
        self.dialog_result = None
        self.file_placement_result = None
        self.selected_work_folder = None
        self.folder_selection_completed = False
    
    # レガシープロパティ（既存コードとの互換性維持）
    @property
    def google_client(self):
        """GoogleSheetClientへのレガシーアクセス"""
        return self.processing_engine.google_client
    
    @property
    def file_manager(self):
        """FileManagerへのレガシーアクセス"""
        return self.processing_engine.file_manager
    
    @property
    def word_processor(self):
        """WordProcessorへのレガシーアクセス"""
        return self.processing_engine.word_processor
    
    @property
    def web_client(self):
        """WebClientへのレガシーアクセス"""
        return self.processing_engine.web_client
    
    @property
    def email_monitor(self):
        """EmailMonitorへのレガシーアクセス"""
        return self.processing_engine.email_monitor
    
    @property
    def api_processor(self):
        """ApiProcessorへのレガシーアクセス"""
        return self.processing_engine.api_processor
    
    # メインメソッド（新アーキテクチャに委譲）
    def process_n_codes(self, n_codes: List[str]):
        """
        複数のN-codeを処理（オーケストレーターに委譲）
        
        Args:
            n_codes: 処理するN-codeのリスト
        """
        return self.orchestrator.process_n_codes(n_codes)
    
    def process_single_n_code(self, n_code: str):
        """
        単一のN-codeを処理（オーケストレーターに委譲）
        
        Args:
            n_code: 処理するN-code
        """
        return self.orchestrator.process_single_n_code(n_code)
    
    # ユーティリティメソッド（オーケストレーターに委譲）
    def emit_log(self, message: str, level: str = "INFO"):
        """ログメッセージを送信"""
        self.orchestrator.emit_log(message, level)
    
    def emit_progress(self, value: int):
        """進捗を送信"""
        self.orchestrator.emit_progress(value)
    
    def emit_status(self, message: str):
        """ステータスを送信"""
        self.orchestrator.emit_status(message)
    
    # レガシーメソッド（オーケストレーターに委譲）
    def set_selected_work_folder(self, folder_path: str):
        """選択された作業フォルダを設定（レガシー互換）"""
        self.orchestrator.set_selected_work_folder(folder_path)
        # レガシー変数も更新
        self.selected_work_folder = Path(folder_path) if folder_path else None
        self.folder_selection_completed = True
    
    def on_file_placement_confirmed(self, selected_files: List[Path]):
        """ファイル配置確認の結果を受信（レガシー互換）"""
        self.orchestrator.on_file_placement_confirmed(selected_files)
        # レガシー変数も更新
        self.file_placement_result = selected_files
    
    def cleanup(self):
        """リソースをクリーンアップ"""
        self.processing_engine.cleanup()
    
    # 新機能メソッド（新アーキテクチャの恩恵）
    def get_configuration_summary(self) -> Dict[str, Any]:
        """
        現在の設定サマリーを取得
        
        Returns:
            設定サマリー辞書
        """
        return self.config_manager.get_configuration_summary()
    
    def validate_configuration(self) -> List[str]:
        """
        設定の妥当性を検証
        
        Returns:
            検証エラーメッセージのリスト
        """
        return self.config_manager.validate_configuration()
    
    def update_process_mode(self, new_mode: str):
        """
        処理方式を動的に変更
        
        Args:
            new_mode: 新しい処理方式
        """
        self.config_manager.set_process_mode(new_mode)
        self.process_mode = new_mode  # レガシー変数も更新
        self.logger.info(f"処理方式を変更: {new_mode}")
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        処理統計情報を取得（将来の機能拡張用）
        
        Returns:
            処理統計辞書
        """
        return {
            'architecture_version': '3-tier-refactored',
            'configuration': self.get_configuration_summary(),
            'validation_status': len(self.validate_configuration()) == 0,
            'available_features': [
                'n_code_processing',
                'multi_mode_conversion',
                'dynamic_configuration',
                'enhanced_logging'
            ]
        }
    
    def __str__(self) -> str:
        """オブジェクトの文字列表現"""
        return f"WorkflowProcessor(refactored, {self.config_manager})"


class WorkflowOrchestrator(QObject):
    """
    ワークフロー制御専門クラス (150行目標)
    責務: フロー制御、ダイアログ管理、ユーザーインタラクション
    """
    
    # シグナル定義（フロー制御用）
    log_message = pyqtSignal(str, str)  # message, level
    progress_updated = pyqtSignal(int)  # progress value
    status_updated = pyqtSignal(str)  # status message
    confirmation_needed = pyqtSignal(str, str, object)  # title, message, callback
    folder_selection_needed = pyqtSignal(object, str, object)  # repo_path, repo_name, default_folder
    file_placement_confirmation_needed = pyqtSignal(str, list, object)  # honbun_folder_path, file_list, callback
    warning_dialog_needed = pyqtSignal(list, str)  # messages, result_type
    
    def __init__(self, config_manager: 'ConfigurationManager', processing_engine: 'ProcessingEngine'):
        """
        ワークフローオーケストレーター初期化
        
        Args:
            config_manager: 設定管理インスタンス
            processing_engine: 処理エンジンインスタンス
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.config_manager = config_manager
        self.processing_engine = processing_engine
        
        # ダイアログ結果の保存用
        self.dialog_result = None
        self.file_placement_result = None
        self.selected_work_folder = None
        self.folder_selection_completed = False
        
        # 処理エンジンのシグナルを転送
        self._connect_processing_engine_signals()
        
        self.logger.info("[ORCHESTRATOR] WorkflowOrchestrator初期化完了")
    
    def _connect_processing_engine_signals(self):
        """処理エンジンのシグナルをオーケストレーターに転送"""
        self.processing_engine.log_message.connect(self.log_message.emit)
        self.processing_engine.progress_updated.connect(self.progress_updated.emit)
        self.processing_engine.warning_dialog_needed.connect(self.warning_dialog_needed.emit)
    
    def process_n_codes(self, n_codes: List[str]):
        """
        複数のN-codeを処理（メインエントリポイント）
        
        Args:
            n_codes: 処理するN-codeのリスト
        """
        total = len(n_codes)
        self.emit_log(f"処理開始: {total}個のN-code", "INFO")
        
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
        単一のN-codeを処理（フロー制御）
        
        Args:
            n_code: 処理するN-code
        """
        self.logger.info(f"N-code処理開始: {n_code}")
        
        # 1. リポジトリ情報取得
        repo_info = self.processing_engine.get_repository_info(n_code)
        if not repo_info:
            raise ValueError(f"N-code {n_code} がGoogleシートに見つかりません")
        
        repo_name = repo_info['repository_name']
        self.emit_log(f"リポジトリ名: {repo_name}", "INFO")
        
        # 2. リポジトリフォルダ検索
        repo_path = self.processing_engine.find_repository_folder(repo_name)
        if not repo_path:
            raise ValueError(f"リポジトリフォルダが見つかりません: {repo_name}")
        
        # 3. 作業フォルダ選択（インタラクティブ）
        work_folder = self._select_work_folder_interactive(repo_path, repo_name)
        if not work_folder:
            # フォールバック: ReVIEWフォルダが存在すればそれを使用
            review_folder = repo_path / "ReVIEW"
            if review_folder.exists():
                self.emit_log(f"フォールバック: ReVIEWフォルダを使用: {review_folder}", "WARNING")
                work_folder = review_folder
            else:
                raise ValueError("作業フォルダが選択されませんでした")
        
        # 4. ZIPファイル作成
        zip_path = self.processing_engine.create_work_zip(work_folder)
        
        # 5. 変換処理実行
        conversion_result = self.processing_engine.execute_conversion(zip_path)
        if not conversion_result['success']:
            raise ValueError(f"変換処理に失敗: {conversion_result['error']}")
        
        # 6. ファイル配置確認（インタラクティブ）
        placement_result = self._handle_file_placement_interactive(n_code, conversion_result['files'])
        if not placement_result:
            raise ValueError("ファイル配置がキャンセルされました")
        
        self.emit_log(f"✓ {n_code} の処理が完了しました", "INFO")
    
    def _select_work_folder_interactive(self, repo_path: Path, repo_name: str) -> Optional[Path]:
        """
        作業フォルダの対話的選択
        
        Args:
            repo_path: リポジトリパス
            repo_name: リポジトリ名
            
        Returns:
            選択された作業フォルダパス
        """
        self.emit_log("作業フォルダを検索中...", "INFO")
        
        # デフォルト作業フォルダを取得
        default_work_folder = self.processing_engine.find_default_work_folder(repo_path, repo_name)
        
        # リポジトリ内容確認のため、常にダイアログを表示
        self.emit_log("リポジトリ内容の確認が必要です", "INFO")
        
        # フォルダ選択ダイアログを表示
        self.selected_work_folder = None
        self.folder_selection_completed = False
        self.folder_selection_needed.emit(repo_path, repo_name, default_work_folder)
        
        # 結果を待機（タイムアウト60秒に延長）
        self._wait_for_dialog_result('folder_selection_completed', 60)
        
        # タイムアウト時のフォールバック処理
        if not self.folder_selection_completed and default_work_folder:
            self.emit_log(f"タイムアウト時にデフォルトフォルダを使用: {default_work_folder}", "WARNING")
            return default_work_folder
        
        return self.selected_work_folder
    
    def _handle_file_placement_interactive(self, n_code: str, processed_files: List[Path]) -> bool:
        """
        ファイル配置の対話的処理
        
        Args:
            n_code: N-code
            processed_files: 処理済みファイルリスト
            
        Returns:
            配置が成功した場合True
        """
        # 本文フォルダ特定
        honbun_folder = self.processing_engine.find_honbun_folder(n_code)
        if not honbun_folder:
            raise ValueError(f"本文フォルダが見つかりません: {n_code}")
        
        # ファイル配置確認ダイアログ表示
        selected_files = self._show_file_placement_confirmation(str(honbun_folder), processed_files)
        if not selected_files:
            return False
        
        # ファイル配置実行
        return self.processing_engine.copy_files_to_folder(selected_files, honbun_folder)
    
    def _show_file_placement_confirmation(self, honbun_folder_path: str, file_list: List[Path]) -> List[Path]:
        """
        ファイル配置確認ダイアログを表示
        
        Args:
            honbun_folder_path: 本文フォルダのパス
            file_list: 処理済みファイルのリスト
            
        Returns:
            選択されたファイルのリスト
        """
        self.file_placement_result = None
        self.file_placement_confirmation_needed.emit(honbun_folder_path, file_list, self.on_file_placement_confirmed)
        
        # 結果を待機
        self._wait_for_dialog_result('file_placement_result', 60)
        
        return self.file_placement_result if self.file_placement_result else []
    
    def _wait_for_dialog_result(self, result_attribute: str, timeout: int):
        """
        ダイアログ結果の待機処理
        
        Args:
            result_attribute: 結果を保存する属性名
            timeout: タイムアウト時間（秒）
        """
        import time
        from PyQt6.QtCore import QCoreApplication
        
        start_time = time.time()
        last_log_time = start_time
        
        while (time.time() - start_time) < timeout:
            # 定期的に待機状況をログ出力
            if (time.time() - last_log_time) >= 10:
                remaining = timeout - (time.time() - start_time)
                self.emit_log(f"ダイアログ応答待機中... (残り{remaining:.0f}秒)", "INFO")
                last_log_time = time.time()
            
            if result_attribute == 'folder_selection_completed' and self.folder_selection_completed:
                self.emit_log(f"ダイアログ応答受信: {result_attribute}", "INFO")
                break
            elif result_attribute == 'file_placement_result' and self.file_placement_result is not None:
                self.emit_log(f"ダイアログ応答受信: {result_attribute}", "INFO")
                break
            
            time.sleep(0.1)
            QCoreApplication.processEvents()
        else:
            # タイムアウト発生
            elapsed = time.time() - start_time
            self.emit_log(f"ダイアログ応答タイムアウト: {result_attribute} ({elapsed:.1f}秒経過)", "ERROR")
    
    def set_selected_work_folder(self, folder_path: str):
        """選択された作業フォルダを設定"""
        self.selected_work_folder = Path(folder_path) if folder_path else None
        self.folder_selection_completed = True
    
    def on_file_placement_confirmed(self, selected_files: List[Path]):
        """ファイル配置確認の結果を受信"""
        self.file_placement_result = selected_files
        self.emit_log(f"ファイル配置確認結果: {len(selected_files)}個のファイルを選択", "INFO")
    
    def emit_log(self, message: str, level: str = "INFO"):
        """ログメッセージを送信"""
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


class ProcessingEngine(QObject):
    """
    処理実行専門クラス (200行目標)
    責務: 実際の処理、API/メール/従来方式分岐、ファイル操作
    """
    
    # シグナル定義（処理結果用）
    log_message = pyqtSignal(str, str)  # message, level
    progress_updated = pyqtSignal(int)  # progress value
    warning_dialog_needed = pyqtSignal(list, str)  # messages, result_type
    
    def __init__(self, config_manager: 'ConfigurationManager'):
        """
        処理エンジン初期化
        
        Args:
            config_manager: 設定管理インスタンス
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.config_manager = config_manager
        
        # 処理コンポーネントの遅延初期化
        self._google_client = None
        self._file_manager = None
        self._word_processor = None
        self._web_client = None
        self._email_monitor = None
        self._api_processor = None
        
        self.logger.info("[ENGINE] ProcessingEngine初期化完了")
    
    @property
    def google_client(self):
        """GoogleSheetClient の遅延初期化"""
        if self._google_client is None:
            from core.google_sheet import GoogleSheetClient
            self._google_client = GoogleSheetClient()
        return self._google_client
    
    @property
    def file_manager(self):
        """FileManager の遅延初期化"""
        if self._file_manager is None:
            from core.file_manager import FileManager
            self._file_manager = FileManager()
        return self._file_manager
    
    @property
    def word_processor(self):
        """WordProcessor の遅延初期化（DI対応）"""
        if self._word_processor is None:
            from core.word_processor import WordProcessor
            from core.di_container import get_container
            
            # DIコンテナからWordProcessorを取得
            try:
                container = get_container()
                self._word_processor = container.get_service(WordProcessor)
            except Exception as e:
                self.logger.warning(f"DIコンテナからWordProcessor取得失敗: {e}")
                # フォールバック：ConfigurationProviderを手動で作成
                from core.configuration_provider import ConfigurationProvider
                config_provider = ConfigurationProvider()
                self._word_processor = WordProcessor(config_provider)
        return self._word_processor
    
    @property
    def web_client(self):
        """WebClient の遅延初期化"""
        if self._web_client is None:
            from core.web_client import WebClient
            self._web_client = WebClient()
        return self._web_client
    
    @property
    def email_monitor(self):
        """EmailMonitor の遅延初期化（処理方式に基づく実装選択）"""
        if self._email_monitor is None:
            process_mode = self.config_manager.get_process_mode()
            email_config = self.config_manager.get_email_config()
            
            is_gmail_api_mode = (process_mode == "gmail_api" or 
                                email_config.get('password') == "GMAIL_API")
            
            if is_gmail_api_mode:
                self.logger.info("Gmail APIを使用してメール監視を初期化します")
                from core.gmail_oauth_monitor import GmailOAuthMonitor
                from core.gmail_oauth_exe_helper import gmail_oauth_helper
                
                if gmail_oauth_helper.is_exe:
                    self._email_monitor = GmailOAuthMonitor(credentials_path=None)
                else:
                    credentials_path = email_config.get('gmail_credentials_path', 'config/gmail_oauth_credentials.json')
                    self._email_monitor = GmailOAuthMonitor(credentials_path)
                
                self._email_monitor.authenticate()
            else:
                # 従来のIMAP使用
                if email_config.get('password') and email_config.get('password') != "GMAIL_API":
                    self.logger.info("IMAPを使用してメール監視を初期化します")
                    from core.email_monitor import EmailMonitor
                    self._email_monitor = EmailMonitor(email_config['address'], email_config['password'])
                    self._email_monitor.connect()
                else:
                    self.logger.warning("メールパスワードが設定されていません")
                    return None
        return self._email_monitor
    
    @property
    def api_processor(self):
        """ApiProcessor の遅延初期化（Phase 3-2: DI Container統合対応）"""
        try:
            if self._api_processor is None:
                self.logger.info("[API_PROCESSOR] Starting lazy initialization...")
                
                from core.api_processor import ApiProcessor
                from core.di_container import get_container
                
                # DI Containerから適切にインスタンス化（Enhanced Error Handling）
                try:
                    container = get_container()
                    self.logger.info(f"[API_PROCESSOR] DI Container obtained: {type(container)}")
                    
                    # DI Container統合の安定性向上: get_service()メソッドを使用
                    self._api_processor = container.get_service(ApiProcessor)
                    self.logger.info(f"[API_PROCESSOR] ApiProcessor instance created via DI: {type(self._api_processor)}")
                    
                    # DI統合の成功を記録
                    self.logger.info("[API_PROCESSOR] DI Container integration successful")
                    
                except Exception as di_error:
                    self.logger.error(f"[API_PROCESSOR] DI Container integration error: {di_error}", exc_info=True)
                    
                    # エラー詳細の分析
                    if "get_service" in str(di_error):
                        self.logger.error("[API_PROCESSOR] DI method call error detected")
                    elif "not registered" in str(di_error):
                        self.logger.error("[API_PROCESSOR] Service registration missing in DI container")
                    
                    # Fallback: Direct instantiation with enhanced logging
                    self.logger.warning("[API_PROCESSOR] Fallback to direct instantiation due to DI error")
                    try:
                        self._api_processor = ApiProcessor(self.config_manager)
                        self.logger.info(f"[API_PROCESSOR] Direct instantiation successful: {type(self._api_processor)}")
                    except Exception as fallback_error:
                        self.logger.error(f"[API_PROCESSOR] Direct instantiation also failed: {fallback_error}", exc_info=True)
                        raise AttributeError(f"Failed to initialize ApiProcessor via both DI and direct instantiation: {di_error}") from di_error
                
                # シグナルを接続
                if hasattr(self._api_processor, 'log_message'):
                    self._api_processor.log_message.connect(self.log_message.emit)
                    self.logger.debug("[API_PROCESSOR] log_message signal connected")
                    
                if hasattr(self._api_processor, 'progress_updated'):
                    self._api_processor.progress_updated.connect(self.progress_updated.emit)
                    self.logger.debug("[API_PROCESSOR] progress_updated signal connected")
                    
                if hasattr(self._api_processor, 'warning_dialog_needed'):
                    self._api_processor.warning_dialog_needed.connect(self.warning_dialog_needed.emit)
                    self.logger.debug("[API_PROCESSOR] warning_dialog_needed signal connected")
                
                self.logger.info("[API_PROCESSOR] Initialization complete")
                
            return self._api_processor
            
        except Exception as prop_error:
            self.logger.error(f"[API_PROCESSOR] Property access error: {prop_error}", exc_info=True)
            # 最後のフォールバック: エラーを上位に伝播
            raise AttributeError(f"api_processor property failed: {prop_error}") from prop_error
    
    def get_repository_info(self, n_code: str) -> Optional[Dict[str, str]]:
        """
        GoogleシートからN-codeのリポジトリ情報を取得
        
        Args:
            n_code: 検索するN-code
            
        Returns:
            リポジトリ情報（見つからない場合はNone）
        """
        self.emit_log(f"Googleシートから {n_code} を検索中...", "INFO")
        return self.google_client.search_n_code(n_code)
    
    def find_repository_folder(self, repo_name: str) -> Optional[Path]:
        """
        リポジトリフォルダを検索
        
        Args:
            repo_name: リポジトリ名
            
        Returns:
            リポジトリフォルダパス（見つからない場合はNone）
        """
        self.emit_log(f"リポジトリフォルダを検索中: {repo_name}", "INFO")
        return self.file_manager.find_repository_folder(repo_name)
    
    def find_default_work_folder(self, repo_path: Path, repo_name: str) -> Optional[Path]:
        """
        デフォルト作業フォルダを検索
        
        Args:
            repo_path: リポジトリパス
            repo_name: リポジトリ名
            
        Returns:
            デフォルト作業フォルダパス
        """
        return self.file_manager.find_work_folder_interactive(repo_path, repo_name)
    
    def create_work_zip(self, work_folder: Path) -> Path:
        """
        作業フォルダからZIPファイルを作成
        
        Args:
            work_folder: 作業フォルダパス
            
        Returns:
            作成されたZIPファイルのパス
        """
        self.emit_log("ZIPファイルを作成中...", "INFO")
        return self.file_manager.create_zip(work_folder)
    
    def execute_conversion(self, zip_path: Path) -> Dict[str, Any]:
        """
        変換処理を実行（処理方式に応じて分岐）
        
        Args:
            zip_path: 変換対象ZIPファイルパス
            
        Returns:
            変換結果
            {
                'success': bool,
                'files': List[Path],  # 変換済みファイル
                'error': str,         # エラーメッセージ（失敗時）
                'warnings': List[str] # 警告メッセージ
            }
        """
        process_mode = self.config_manager.get_process_mode()
        self.logger.info(f"変換処理開始: {process_mode}方式")
        
        if process_mode == "api":
            return self._execute_api_conversion(zip_path)
        else:
            return self._execute_traditional_conversion(zip_path)
    
    def _execute_api_conversion(self, zip_path: Path) -> Dict[str, Any]:
        """API方式での変換処理（Enhanced Debug対応）"""
        self.emit_log("API方式で変換処理を開始...", "INFO")
        self.logger.info(f"[API_CONVERSION] ZIP path: {zip_path}")
        self.logger.info(f"[API_CONVERSION] ZIP exists: {zip_path.exists()}")
        self.logger.info(f"[API_CONVERSION] ZIP size: {zip_path.stat().st_size if zip_path.exists() else 'N/A'} bytes")
        
        try:
            # APIプロセッサーのインスタンス化を確認（Enhanced Debug）
            self.logger.info("[API_CONVERSION] API processor initialization check...")
            self.logger.info(f"[API_CONVERSION] ProcessingEngine type: {type(self)}")
            self.logger.info(f"[API_CONVERSION] hasattr _api_processor: {hasattr(self, '_api_processor')}")
            self.logger.info(f"[API_CONVERSION] hasattr api_processor: {hasattr(self, 'api_processor')}")
            self.logger.info(f"[API_CONVERSION] _api_processor value: {getattr(self, '_api_processor', 'NOT_FOUND')}")
            
            # プロパティ情報の詳細検査
            prop_descriptor = getattr(type(self), 'api_processor', None)
            self.logger.info(f"[API_CONVERSION] api_processor descriptor: {prop_descriptor}")
            self.logger.info(f"[API_CONVERSION] descriptor type: {type(prop_descriptor)}")
            
            api_proc = self.api_processor
            self.logger.info(f"[API_CONVERSION] API processor type: {type(api_proc)}")
            
            # API処理実行
            self.logger.info("[API_CONVERSION] Starting ZIP file processing...")
            success, download_path, warnings = api_proc.process_zip_file(zip_path)
            self.logger.info(f"[API_CONVERSION] Processing result - success: {success}, download_path: {download_path}")
            if warnings:
                self.logger.info(f"[API_CONVERSION] Warnings ({len(warnings)}): {warnings[:3]}...")  # 最初の3つのみログ
            
            if not success:
                # Enhanced error handling対応: 詳細なエラー情報を表示
                self.logger.error(f"[API_CONVERSION] Processing failed with {len(warnings) if warnings else 0} warnings")
                for i, warning in enumerate(warnings[:5] if warnings else []):  # 最初の5つまで詳細ログ
                    self.logger.error(f"[API_CONVERSION] Warning {i+1}: {warning}")
                
                # サーバーエラー判定とユーザーガイダンス
                is_server_error = warnings and any("サーバー設定エラー" in str(msg) for msg in warnings)
                if is_server_error:
                    self.emit_log("サーバーエラー検出 - ユーザーガイダンス表示中...", "INFO")
                    # PyQtシグナルの処理時間を確保（enhanced error handlingのガイダンス表示）
                    import time
                    time.sleep(0.5)  # 500ms待機でシグナル処理時間を確保
                    self.emit_log("詳細なエラー情報とガイダンスを上記で確認してください", "WARNING")
                
                # エラー種別の判定
                error_type = "サーバー側エラー" if is_server_error else "アプリ側エラー"
                self.emit_log(f"エラー種別判定: {error_type}", "INFO")
                
                return {
                    'success': False,
                    'files': [],
                    'error': f"API変換処理が失敗しました [{error_type}] ({', '.join(str(w)[:100] for w in warnings[:3]) if warnings else '詳細不明'})",
                    'warnings': warnings or []
                }
            
            if not download_path:
                return {
                    'success': False,
                    'files': [],
                    'error': "変換ファイルのダウンロードに失敗しました",
                    'warnings': warnings or []
                }
            
            # ZIPファイルを処理（展開 + 1行目削除）
            processed_files = self.word_processor.process_zip_file(download_path)
            
            return {
                'success': True,
                'files': processed_files,
                'error': '',
                'warnings': warnings or []
            }
        
        except Exception as e:
            # 詳細なエラー情報をログに記録
            self.logger.error(f"[API_CONVERSION] Exception occurred: {type(e).__name__}: {e}", exc_info=True)
            self.emit_log(f"API処理で例外が発生: {type(e).__name__}: {str(e)}", "ERROR")
            
            # 属性エラーの場合は特別な処理（Enhanced Analysis）
            if isinstance(e, AttributeError):
                self.logger.error(f"[API_CONVERSION] AttributeError details - object: {type(self)}, missing attr: api_processor")
                
                # 完全な属性リスト（api関連）
                api_attrs = [attr for attr in dir(self) if 'api' in attr.lower()]
                self.logger.error(f"[API_CONVERSION] Available api attributes: {api_attrs}")
                
                # プロパティとメソッドの分類
                properties = []
                methods = []
                for attr in api_attrs:
                    attr_value = getattr(type(self), attr, None)
                    if isinstance(attr_value, property):
                        properties.append(attr)
                    elif callable(getattr(self, attr, None)):
                        methods.append(attr)
                
                self.logger.error(f"[API_CONVERSION] Properties: {properties}")
                self.logger.error(f"[API_CONVERSION] Methods: {methods}")
                
                # 直接アクセス試行（Fallback Strategy）
                try:
                    if hasattr(self, '_api_processor') and self._api_processor is not None:
                        self.logger.error("[API_CONVERSION] Fallback: Using _api_processor directly")
                        fallback_api_proc = self._api_processor
                        self.emit_log("Fallback: _api_processorを直接使用", "WARNING")
                        # この場合は処理を続行する可能性を考慮
                    else:
                        self.logger.error("[API_CONVERSION] Fallback failed: _api_processor is None or missing")
                except Exception as fallback_error:
                    self.logger.error(f"[API_CONVERSION] Fallback error: {fallback_error}")
                
                self.emit_log(f"属性エラー検出: ProcessingEngine.api_processor が見つかりません", "ERROR")
            
            return {
                'success': False,
                'files': [],
                'error': f"API変換処理でエラーが発生: {type(e).__name__}: {str(e)}",
                'warnings': []
            }
    
    def _execute_traditional_conversion(self, zip_path: Path) -> Dict[str, Any]:
        """従来方式/Gmail API方式での変換処理"""
        process_mode = self.config_manager.get_process_mode()
        mode_text = "Gmail API方式" if process_mode == "gmail_api" else "従来方式"
        self.emit_log(f"{mode_text}で処理を開始...", "INFO")
        
        try:
            # ファイルをアップロード（処理方式を渡す）
            email_config = self.config_manager.get_email_config()
            upload_success = self.web_client.upload_file(zip_path, email_config['address'], process_mode)
            
            if not upload_success:
                return {
                    'success': False,
                    'files': [],
                    'error': "ファイルのアップロードに失敗しました",
                    'warnings': []
                }
            
            # メールを監視
            if not email_config.get('password'):
                return {
                    'success': False,
                    'files': [],
                    'error': "メールパスワードが設定されていないため、手動でダウンロードしてください",
                    'warnings': []
                }
            
            self.emit_log("変換完了メールを待機中...", "INFO")
            
            # メール監視処理
            if hasattr(self.email_monitor, 'wait_for_email'):
                try:
                    download_url = self.email_monitor.wait_for_email(
                        subject_pattern="Re:VIEW to 超原稿用紙",
                        since_time=None,
                        from_address="kanazawa@nextpublishing.jp"
                    )
                except TypeError:
                    from utils.constants import EMAIL_SENDERS, EMAIL_SUBJECTS
                    download_url = self.email_monitor.wait_for_email(
                        subject_pattern=EMAIL_SUBJECTS['REVIEW_CONVERSION'],
                        from_address=EMAIL_SENDERS['REVIEW_CONVERSION']
                    )
            else:
                from utils.constants import EMAIL_SENDERS
                download_url = self.email_monitor.wait_for_email(
                    from_address=EMAIL_SENDERS['REVIEW_CONVERSION']
                )
            
            if not download_url:
                return {
                    'success': False,
                    'files': [],
                    'error': "タイムアウト: メールが届きませんでした",
                    'warnings': []
                }
            
            # ファイルをダウンロード
            self.emit_log("変換済みファイルをダウンロード中...", "INFO")
            download_path = self.file_manager.temp_dir / f"converted_{zip_path.stem}.zip"
            download_success = self.web_client.download_file(download_url, download_path)
            
            if not download_success:
                return {
                    'success': False,
                    'files': [],
                    'error': "ファイルのダウンロードに失敗しました",
                    'warnings': []
                }
            
            # ZIPファイルを処理
            processed_files = self.word_processor.process_zip_file(download_path)
            
            return {
                'success': True,
                'files': processed_files,
                'error': '',
                'warnings': []
            }
            
        except Exception as e:
            self.logger.error(f"{mode_text}変換処理エラー: {e}", exc_info=True)
            return {
                'success': False,
                'files': [],
                'error': f"{mode_text}変換処理でエラーが発生: {str(e)}",
                'warnings': []
            }
    
    def find_honbun_folder(self, n_code: str) -> Optional[Path]:
        """
        N-codeから本文フォルダを特定
        
        Args:
            n_code: N-code
            
        Returns:
            本文フォルダパス（見つからない場合はNone）
        """
        ncode_folder = self.word_processor.find_ncode_folder(n_code)
        if not ncode_folder:
            return None
        
        return self.word_processor.find_honbun_folder(ncode_folder)
    
    def copy_files_to_folder(self, files: List[Path], target_folder: Path) -> bool:
        """
        ファイルを指定フォルダにコピー
        
        Args:
            files: コピー対象ファイルリスト
            target_folder: コピー先フォルダ
            
        Returns:
            コピーが成功した場合True
        """
        try:
            import shutil
            
            # ターゲットフォルダが存在しない場合は作成
            target_folder.mkdir(parents=True, exist_ok=True)
            self.emit_log(f"本文フォルダを確認/作成: {target_folder}", "INFO")
            
            success_count = 0
            for file_path in files:
                try:
                    target_path = target_folder / file_path.name
                    shutil.copy2(file_path, target_path)
                    success_count += 1
                    self.emit_log(f"ファイルコピー完了: {file_path.name}", "INFO")
                except Exception as e:
                    self.emit_log(f"ファイルコピーエラー {file_path.name}: {e}", "ERROR")
            
            self.emit_log(f"ファイル配置完了: {success_count}/{len(files)} ファイル", "INFO")
            return success_count > 0
            
        except Exception as e:
            self.emit_log(f"ファイル配置処理エラー: {e}", "ERROR")
            return False
    
    def emit_log(self, message: str, level: str = "INFO"):
        """ログメッセージを送信"""
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
    
    def cleanup(self):
        """リソースをクリーンアップ"""
        if self._email_monitor:
            self._email_monitor.close()
        if self._web_client:
            self._web_client.close()
        if self._file_manager:
            self._file_manager.cleanup_temp_files()


class ConfigurationManager:
    """
    設定・状態管理専門クラス (145行目標)
    責務: 設定管理、状態管理、リソース管理
    """
    
    def __init__(self, email_address: str = None, email_password: str = None, process_mode: str = "traditional"):
        """
        設定管理初期化
        
        Args:
            email_address: メールアドレス（省略時は設定から取得）
            email_password: メールパスワード
            process_mode: 処理方式 ("traditional", "api", "gmail_api")
        """
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.process_mode = process_mode
        
        # メール設定（環境変数を優先）
        email_config = self.config.get_email_config()
        self.email_address = email_address or os.getenv('GMAIL_ADDRESS') or email_config.get('default_address')
        self.email_password = email_password or os.getenv('GMAIL_APP_PASSWORD')
        
        self.logger.info(f"[CONFIG] ConfigurationManager初期化完了")
        self.logger.info(f"[CONFIG] process_mode: {process_mode}")
        self.logger.info(f"[CONFIG] email_address: {self.email_address}")
        self.logger.info(f"[CONFIG] has email_password: {self.email_password is not None}")
    
    def get_process_mode(self) -> str:
        """
        処理方式を取得
        
        Returns:
            処理方式 ("traditional", "api", "gmail_api")
        """
        return self.process_mode
    
    def set_process_mode(self, mode: str):
        """
        処理方式を設定
        
        Args:
            mode: 新しい処理方式
        """
        if mode not in ["traditional", "api", "gmail_api"]:
            raise ValueError(f"無効な処理方式: {mode}")
        
        self.process_mode = mode
        self.logger.info(f"[CONFIG] 処理方式を変更: {mode}")
    
    def get_email_config(self) -> Dict[str, str]:
        """
        メール設定を取得
        
        Returns:
            メール設定辞書
        """
        email_config = self.config.get_email_config()
        return {
            'address': self.email_address,
            'password': self.email_password,
            'gmail_credentials_path': email_config.get('gmail_credentials_path', 'config/gmail_oauth_credentials.json')
        }
    
    def update_email_config(self, address: str = None, password: str = None):
        """
        メール設定を更新
        
        Args:
            address: 新しいメールアドレス
            password: 新しいメールパスワード
        """
        if address:
            self.email_address = address
            self.logger.info(f"[CONFIG] メールアドレスを更新: {address}")
        
        if password:
            self.email_password = password
            self.logger.info(f"[CONFIG] メールパスワードを更新")
    
    def get_temp_directory(self) -> Path:
        """
        一時ディレクトリを取得
        
        Returns:
            一時ディレクトリパス
        """
        return Path(self.config.get('temp_dir', '/tmp/techzip'))
    
    def get_api_config(self) -> Dict[str, Any]:
        """
        API設定を取得
        
        Returns:
            API設定辞書
        """
        return self.config.get('api', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """
        処理設定を取得
        
        Returns:
            処理設定辞書
        """
        return {
            'process_mode': self.process_mode,
            'email_config': self.get_email_config(),
            'temp_directory': self.get_temp_directory(),
            'api_config': self.get_api_config(),
            'timeout_settings': self.config.get('timeouts', {}),
            'retry_settings': self.config.get('retry', {})
        }
    
    def validate_configuration(self) -> List[str]:
        """
        設定の妥当性を検証
        
        Returns:
            検証エラーメッセージのリスト（空の場合は正常）
        """
        errors = []
        
        # 基本設定チェック
        if not self.email_address:
            errors.append("メールアドレスが設定されていません")
        
        # 処理方式別チェック
        if self.process_mode == "api":
            api_config = self.get_api_config()
            if not api_config.get('username') or not api_config.get('password'):
                errors.append("API方式にはusernameとpasswordが必要です")
        
        elif self.process_mode in ["traditional", "gmail_api"]:
            if self.process_mode == "traditional" and not self.email_password:
                errors.append("従来方式にはメールパスワードが必要です")
            
            elif self.process_mode == "gmail_api":
                email_config = self.config.get_email_config()
                credentials_path = email_config.get('gmail_credentials_path')
                if credentials_path and not Path(credentials_path).exists():
                    errors.append(f"Gmail認証ファイルが見つかりません: {credentials_path}")
        
        # ディレクトリ存在チェック
        temp_dir = self.get_temp_directory()
        try:
            temp_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"一時ディレクトリの作成に失敗: {temp_dir} ({e})")
        
        return errors
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """
        設定サマリーを取得
        
        Returns:
            設定サマリー辞書
        """
        email_config = self.get_email_config()
        return {
            'process_mode': self.process_mode,
            'email_address': self.email_address,
            'has_email_password': bool(self.email_password),
            'temp_directory': str(self.get_temp_directory()),
            'gmail_credentials_exists': Path(email_config.get('gmail_credentials_path', '')).exists(),
            'validation_errors': self.validate_configuration()
        }
    
    def __str__(self) -> str:
        """設定の文字列表現"""
        summary = self.get_configuration_summary()
        return f"ConfigurationManager(mode={summary['process_mode']}, email={summary['email_address']}, valid={len(summary['validation_errors']) == 0})"
