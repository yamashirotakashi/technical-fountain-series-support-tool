"""
Application Controller - ビジネスロジック統合管理

Phase 3-1: God Object解消の一環として、MainWindowからビジネスロジックを分離。
SOLID原則のSingle Responsibilityに準拠し、アプリケーションの核となる処理を統一管理。
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal
from pathlib import Path

from core.workflow_processor import WorkflowProcessor
from core.api_processor import ApiProcessor
from utils.logger import get_logger

if TYPE_CHECKING:
    from gui.managers.state_manager import StateManager


class ApplicationController(QObject):
    """アプリケーションのビジネスロジック制御
    
    責任:
    - ワークフロー処理の統合管理
    - API処理の制御
    - バックグラウンド処理の調整
    - エラーハンドリングの統一
    
    Note: MainWindowから分離されたビジネスロジック部分
    """
    
    # シグナル定義
    processing_started = pyqtSignal(list)  # n_codes
    processing_finished = pyqtSignal(bool)  # success
    error_occurred = pyqtSignal(str, str)  # message, error_type
    status_changed = pyqtSignal(str)  # status_message
    
    def __init__(self, state_manager: 'StateManager'):
        """ApplicationController初期化
        
        Args:
            state_manager: 状態管理マネージャー
        """
        super().__init__()
        self.state_manager = state_manager
        self.logger = get_logger(__name__)
        
        # プロセッサーインスタンス
        self.workflow_processor: Optional[WorkflowProcessor] = None
        self.api_processor: Optional[ApiProcessor] = None
        
        self.logger.info("ApplicationController initialized")
    
    def process_n_codes(self, n_codes: List[str], email_password: Optional[str] = None,
                       process_mode: str = "api") -> bool:
        """N-codeリストの処理を開始
        
        Args:
            n_codes: 処理するN-codeリスト
            email_password: メール認証パスワード
            process_mode: 処理モード ('api' | 'traditional' | 'gmail_api')
            
        Returns:
            bool: 処理開始成功/失敗
        """
        try:
            self.logger.info(f"Processing {len(n_codes)} N-codes with mode: {process_mode}")
            
            # 状態を処理中に変更
            self.state_manager.set_processing_state(True)
            self.processing_started.emit(n_codes)
            
            # WorkflowProcessorを初期化
            self.workflow_processor = WorkflowProcessor(
                email_password=email_password,
                process_mode=process_mode
            )
            
            # シグナル接続
            self._connect_workflow_signals()
            
            # 処理実行
            self.workflow_processor.process_n_codes(n_codes)
            
            return True
            
        except Exception as e:
            self.logger.error(f"N-code処理開始エラー: {e}", exc_info=True)
            self.error_occurred.emit(f"処理開始エラー: {str(e)}", "PROCESS_START_ERROR")
            self.state_manager.set_processing_state(False)
            return False
    
    def start_error_detection(self, n_codes: List[str]) -> bool:
        """エラー検出処理を開始
        
        Args:
            n_codes: エラー検出対象のN-codeリスト
            
        Returns:
            bool: エラー検出開始成功/失敗
        """
        try:
            self.logger.info(f"Starting error detection for {len(n_codes)} N-codes")
            
            # 状態変更
            self.state_manager.set_error_detection_state(True)
            self.status_changed.emit("エラー検出を開始しています...")
            
            # APIプロセッサーを初期化
            self.api_processor = ApiProcessor()
            
            # エラー検出ロジック実装
            # TODO: 実装詳細をWorkflowProcessorから移行
            
            return True
            
        except Exception as e:
            self.logger.error(f"エラー検出開始エラー: {e}", exc_info=True)
            self.error_occurred.emit(f"エラー検出開始エラー: {str(e)}", "ERROR_DETECTION_START_ERROR")
            self.state_manager.set_error_detection_state(False)
            return False
    
    def start_pdf_post(self, n_code: str) -> bool:
        """PDFポスト処理を開始
        
        Args:
            n_code: 投稿対象のN-code
            
        Returns:
            bool: PDFポスト開始成功/失敗
        """
        try:
            self.logger.info(f"Starting PDF post for N-code: {n_code}")
            
            # PDF投稿ロジック実装
            # TODO: 実装詳細を移行
            
            return True
            
        except Exception as e:
            self.logger.error(f"PDFポスト開始エラー: {e}", exc_info=True)
            self.error_occurred.emit(f"PDFポスト開始エラー: {str(e)}", "PDF_POST_START_ERROR")
            return False
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        try:
            if self.workflow_processor:
                self.workflow_processor.cleanup()
                self.workflow_processor = None
                
            if self.api_processor:
                # API processor cleanup if needed
                self.api_processor = None
                
            # 状態リセット
            self.state_manager.reset_all_states()
            
            self.logger.info("ApplicationController cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}", exc_info=True)
    
    def _connect_workflow_signals(self):
        """WorkflowProcessorのシグナル接続"""
        if not self.workflow_processor:
            return
            
        # WorkflowProcessorのシグナルをApplicationControllerのシグナルに中継
        self.workflow_processor.status_updated.connect(self.status_changed.emit)
        
        # 処理完了シグナルの接続
        self.workflow_processor.finished.connect(self._on_workflow_finished)
    
    def _on_workflow_finished(self):
        """ワークフロー処理完了ハンドラー"""
        try:
            self.state_manager.set_processing_state(False)
            self.processing_finished.emit(True)
            self.status_changed.emit("処理が完了しました")
            
        except Exception as e:
            self.logger.error(f"Workflow finished handler error: {e}", exc_info=True)
            self.processing_finished.emit(False)