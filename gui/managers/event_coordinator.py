"""
Event Coordinator - イベント統合・調整管理

Phase 3-1: God Object解消の一環として、MainWindowから複雑なイベント処理を分離。
SOLID原則のSingle Responsibilityに準拠し、異なるコンポーネント間のイベント調整を担当。
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Dict, List, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
from PyQt6.QtWidgets import QApplication
from dataclasses import dataclass
from datetime import datetime

from utils.logger import get_logger

if TYPE_CHECKING:
    from gui.managers.state_manager import StateManager
    from gui.controllers.application_controller import ApplicationController
    from gui.controllers.window_controller import WindowController


@dataclass
class EventContext:
    """イベントコンテキストデータクラス"""
    event_type: str
    source_component: str
    target_component: str
    data: Any
    timestamp: datetime
    handled: bool = False
    callback: Optional[Callable] = None


class EventCoordinator(QObject):
    """イベント統合・調整管理クラス
    
    責任:
    - コンポーネント間のイベント調整
    - 非同期イベント処理の統合
    - イベントチェーンの管理
    - エラーイベントの統一処理
    
    Note: MainWindowから分離された複雑なイベント処理部分
    """
    
    # 統合イベントシグナル
    event_processed = pyqtSignal(str, object)  # event_type, result
    error_event = pyqtSignal(str, str)  # error_type, message
    async_operation_completed = pyqtSignal(str, bool, object)  # operation_id, success, result
    
    def __init__(self, state_manager: 'StateManager'):
        """EventCoordinator初期化
        
        Args:
            state_manager: 状態管理マネージャー
        """
        super().__init__()
        self.state_manager = state_manager
        self.logger = get_logger(__name__)
        
        # コントローラー参照（後で設定）
        self.app_controller: Optional['ApplicationController'] = None
        self.window_controller: Optional['WindowController'] = None
        
        # イベント処理状態
        self._event_queue: List[EventContext] = []
        self._pending_callbacks: Dict[str, Callable] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # 非同期処理管理
        self._async_operations: Dict[str, Dict[str, Any]] = {}
        
        # イベント処理タイマー
        self._process_timer = QTimer()
        self._process_timer.timeout.connect(self._process_event_queue)
        self._process_timer.setInterval(100)  # 100ms間隔
        
        self.logger.info("EventCoordinator initialized")
    
    def set_controllers(self, app_controller: 'ApplicationController', 
                       window_controller: 'WindowController'):
        """コントローラー参照を設定
        
        Args:
            app_controller: アプリケーションコントローラー
            window_controller: ウィンドウコントローラー
        """
        try:
            self.app_controller = app_controller
            self.window_controller = window_controller
            
            # コントローラーからのシグナル接続
            self._connect_controller_signals()
            
            # イベント処理開始
            self._process_timer.start()
            
            self.logger.info("Controllers set and event processing started")
            
        except Exception as e:
            self.logger.error(f"Controller setup error: {e}", exc_info=True)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """イベントハンドラーを登録
        
        Args:
            event_type: イベントタイプ
            handler: ハンドラー関数
        """
        try:
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []
            
            self._event_handlers[event_type].append(handler)
            self.logger.info(f"Event handler registered for: {event_type}")
            
        except Exception as e:
            self.logger.error(f"Event handler registration error: {e}", exc_info=True)
    
    def emit_event(self, event_type: str, source_component: str, 
                  target_component: str = None, data: Any = None, 
                  callback: Callable = None) -> str:
        """イベントを発行
        
        Args:
            event_type: イベントタイプ
            source_component: 発行元コンポーネント
            target_component: 対象コンポーネント
            data: イベントデータ
            callback: コールバック関数
            
        Returns:
            str: イベントID
        """
        try:
            event_context = EventContext(
                event_type=event_type,
                source_component=source_component,
                target_component=target_component or "all",
                data=data,
                timestamp=datetime.now(),
                callback=callback
            )
            
            event_id = f"{event_type}_{datetime.now().timestamp()}"
            
            # イベントキューに追加
            self._event_queue.append(event_context)
            
            self.logger.info(f"Event emitted: {event_type} from {source_component} to {target_component}")
            return event_id
            
        except Exception as e:
            self.logger.error(f"Event emission error: {e}", exc_info=True)
            return ""
    
    def coordinate_processing_workflow(self, n_codes: List[str], email_password: str = None,
                                     process_mode: str = "api"):
        """処理ワークフローを調整
        
        Args:
            n_codes: 処理対象N-codes
            email_password: メール認証パスワード
            process_mode: 処理モード
        """
        try:
            self.logger.info(f"Coordinating processing workflow for {len(n_codes)} N-codes")
            
            # 1. 状態更新
            self.state_manager.set_processing_state(True, n_codes)
            self.state_manager.set_process_mode(process_mode)
            if email_password:
                self.state_manager.set_email_password(email_password)
            
            # 2. UI更新
            if self.window_controller:
                self.window_controller.update_status_bar("処理を開始しています...")
                self.window_controller.enable_ui_elements(False)
            
            # 3. 処理開始
            if self.app_controller:
                success = self.app_controller.process_n_codes(n_codes, email_password, process_mode)
                
                if not success:
                    self._handle_workflow_error("処理開始に失敗しました")
            
        except Exception as e:
            self.logger.error(f"Processing workflow coordination error: {e}", exc_info=True)
            self._handle_workflow_error(f"ワークフロー調整エラー: {str(e)}")
    
    def coordinate_error_detection_workflow(self, n_codes: List[str]):
        """エラー検出ワークフローを調整
        
        Args:
            n_codes: エラー検出対象N-codes
        """
        try:
            self.logger.info(f"Coordinating error detection workflow for {len(n_codes)} N-codes")
            
            # 1. 状態更新
            self.state_manager.set_error_detection_state(True)
            
            # 2. UI更新
            if self.window_controller:
                self.window_controller.update_status_bar("エラー検出を開始しています...")
                self.window_controller.enable_ui_elements(False)
            
            # 3. エラー検出開始
            if self.app_controller:
                success = self.app_controller.start_error_detection(n_codes)
                
                if not success:
                    self._handle_workflow_error("エラー検出開始に失敗しました")
                    
        except Exception as e:
            self.logger.error(f"Error detection workflow coordination error: {e}", exc_info=True)
            self._handle_workflow_error(f"エラー検出ワークフロー調整エラー: {str(e)}")
    
    def coordinate_folder_selection_workflow(self, repo_path: str, repo_name: str, 
                                           default_folder: str, callback: Callable):
        """フォルダー選択ワークフローを調整
        
        Args:
            repo_path: リポジトリパス
            repo_name: リポジトリ名
            default_folder: デフォルトフォルダー
            callback: 選択完了コールバック
        """
        try:
            self.logger.info(f"Coordinating folder selection workflow for: {repo_name}")
            
            if not self.window_controller:
                callback(None)
                return
            
            # フォルダー選択ダイアログ表示
            selected_folder = self.window_controller.show_folder_selection_dialog(
                repo_path, repo_name, default_folder
            )
            
            # コールバック実行
            callback(selected_folder)
            
        except Exception as e:
            self.logger.error(f"Folder selection workflow coordination error: {e}", exc_info=True)
            callback(None)
    
    def coordinate_file_placement_workflow(self, honbun_folder_path: str, 
                                         file_list: List[str], callback: Callable):
        """ファイル配置ワークフローを調整
        
        Args:
            honbun_folder_path: 本文フォルダーパス
            file_list: ファイルリスト
            callback: 配置完了コールバック
        """
        try:
            self.logger.info(f"Coordinating file placement workflow for {len(file_list)} files")
            
            if not self.window_controller:
                callback(False)
                return
            
            # ファイル配置確認ダイアログ表示
            confirmed = self.window_controller.show_file_placement_confirmation_dialog(
                honbun_folder_path, file_list
            )
            
            # コールバック実行
            callback(confirmed)
            
        except Exception as e:
            self.logger.error(f"File placement workflow coordination error: {e}", exc_info=True)
            callback(False)
    
    def coordinate_async_operation(self, operation_id: str, operation_func: Callable, 
                                 *args, **kwargs) -> str:
        """非同期操作を調整
        
        Args:
            operation_id: 操作ID
            operation_func: 操作関数
            *args: 関数引数
            **kwargs: 関数キーワード引数
            
        Returns:
            str: 操作トラッキングID
        """
        try:
            tracking_id = f"{operation_id}_{datetime.now().timestamp()}"
            
            # 非同期操作情報を記録
            self._async_operations[tracking_id] = {
                "operation_id": operation_id,
                "start_time": datetime.now(),
                "status": "running"
            }
            
            # 非同期実行（簡易実装、実際にはQThreadなど使用）
            QTimer.singleShot(0, lambda: self._execute_async_operation(
                tracking_id, operation_func, args, kwargs
            ))
            
            self.logger.info(f"Async operation coordinated: {tracking_id}")
            return tracking_id
            
        except Exception as e:
            self.logger.error(f"Async operation coordination error: {e}", exc_info=True)
            return ""
    
    def _execute_async_operation(self, tracking_id: str, operation_func: Callable, 
                               args: tuple, kwargs: dict):
        """非同期操作を実行
        
        Args:
            tracking_id: 操作トラッキングID
            operation_func: 操作関数
            args: 関数引数
            kwargs: 関数キーワード引数
        """
        try:
            # 操作実行
            result = operation_func(*args, **kwargs)
            
            # 操作完了
            if tracking_id in self._async_operations:
                self._async_operations[tracking_id]["status"] = "completed"
                self._async_operations[tracking_id]["end_time"] = datetime.now()
                self._async_operations[tracking_id]["result"] = result
            
            # 完了シグナル発信
            operation_id = self._async_operations[tracking_id]["operation_id"]
            self.async_operation_completed.emit(operation_id, True, result)
            
            self.logger.info(f"Async operation completed: {tracking_id}")
            
        except Exception as e:
            self.logger.error(f"Async operation execution error: {e}", exc_info=True)
            
            # エラー状態設定
            if tracking_id in self._async_operations:
                self._async_operations[tracking_id]["status"] = "error"
                self._async_operations[tracking_id]["error"] = str(e)
            
            # エラーシグナル発信
            operation_id = self._async_operations.get(tracking_id, {}).get("operation_id", "unknown")
            self.async_operation_completed.emit(operation_id, False, str(e))
    
    def _connect_controller_signals(self):
        """コントローラーのシグナル接続"""
        try:
            if self.app_controller:
                # アプリケーションコントローラーからのシグナル
                self.app_controller.processing_finished.connect(self._on_processing_finished)
                self.app_controller.error_occurred.connect(self._on_controller_error)
                self.app_controller.status_changed.connect(self._on_status_changed)
            
            if self.window_controller:
                # ウィンドウコントローラーからのシグナル
                self.window_controller.processing_requested.connect(
                    lambda n_codes: self.coordinate_processing_workflow(n_codes)
                )
                self.window_controller.error_detection_requested.connect(
                    self.coordinate_error_detection_workflow
                )
            
            self.logger.info("Controller signals connected")
            
        except Exception as e:
            self.logger.error(f"Controller signal connection error: {e}", exc_info=True)
    
    def _process_event_queue(self):
        """イベントキューを処理"""
        try:
            if not self._event_queue:
                return
            
            # 処理待ちイベントを取得
            events_to_process = [e for e in self._event_queue if not e.handled][:5]  # 最大5個
            
            for event in events_to_process:
                self._process_single_event(event)
                event.handled = True
            
            # 処理済みイベントをキューから削除（履歴は最大100個保持）
            self._event_queue = [e for e in self._event_queue if not e.handled][-100:]
            
        except Exception as e:
            self.logger.error(f"Event queue processing error: {e}", exc_info=True)
    
    def _process_single_event(self, event: EventContext):
        """単一イベントを処理
        
        Args:
            event: イベントコンテキスト
        """
        try:
            # イベントタイプ別処理
            handlers = self._event_handlers.get(event.event_type, [])
            
            for handler in handlers:
                try:
                    result = handler(event)
                    self.event_processed.emit(event.event_type, result)
                    
                except Exception as handler_error:
                    self.logger.error(f"Event handler error: {handler_error}", exc_info=True)
            
            # コールバック実行
            if event.callback:
                try:
                    event.callback(event.data)
                except Exception as callback_error:
                    self.logger.error(f"Event callback error: {callback_error}", exc_info=True)
            
        except Exception as e:
            self.logger.error(f"Single event processing error: {e}", exc_info=True)
    
    def _handle_workflow_error(self, error_message: str):
        """ワークフローエラーを処理
        
        Args:
            error_message: エラーメッセージ
        """
        try:
            # 状態をエラーに設定
            self.state_manager.set_error_state(error_message)
            
            # UI復旧
            if self.window_controller:
                self.window_controller.enable_ui_elements(True)
                self.window_controller.update_status_bar(f"エラー: {error_message}")
            
            # エラーイベント発信
            self.error_event.emit("WORKFLOW_ERROR", error_message)
            
        except Exception as e:
            self.logger.error(f"Workflow error handling error: {e}", exc_info=True)
    
    @pyqtSlot(bool)
    def _on_processing_finished(self, success: bool):
        """処理完了ハンドラー
        
        Args:
            success: 処理成功フラグ
        """
        try:
            # 状態更新
            self.state_manager.set_processing_state(False)
            
            # UI復旧
            if self.window_controller:
                self.window_controller.enable_ui_elements(True)
                status_message = "処理が完了しました" if success else "処理中にエラーが発生しました"
                self.window_controller.update_status_bar(status_message)
            
            self.logger.info(f"Processing finished with success: {success}")
            
        except Exception as e:
            self.logger.error(f"Processing finished handler error: {e}", exc_info=True)
    
    @pyqtSlot(str, str)
    def _on_controller_error(self, message: str, error_type: str):
        """コントローラーエラーハンドラー
        
        Args:
            message: エラーメッセージ
            error_type: エラータイプ
        """
        try:
            self._handle_workflow_error(message)
            self.error_event.emit(error_type, message)
            
        except Exception as e:
            self.logger.error(f"Controller error handler error: {e}", exc_info=True)
    
    @pyqtSlot(str)
    def _on_status_changed(self, status_message: str):
        """ステータス変更ハンドラー
        
        Args:
            status_message: ステータスメッセージ
        """
        try:
            if self.window_controller:
                self.window_controller.update_status_bar(status_message)
                
        except Exception as e:
            self.logger.error(f"Status change handler error: {e}", exc_info=True)
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        try:
            # タイマー停止
            if self._process_timer.isActive():
                self._process_timer.stop()
            
            # イベントキュークリア
            self._event_queue.clear()
            self._pending_callbacks.clear()
            self._event_handlers.clear()
            self._async_operations.clear()
            
            self.logger.info("EventCoordinator cleanup completed")
            
        except Exception as e:
            self.logger.error(f"EventCoordinator cleanup error: {e}", exc_info=True)