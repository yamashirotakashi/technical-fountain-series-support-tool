"""
State Manager - アプリケーション状態統合管理

Phase 3-1: God Object解消の一環として、MainWindowから状態管理ロジックを分離。
SOLID原則のSingle Responsibilityに準拠し、アプリケーション全体の状態を統一管理。
"""
from __future__ import annotations
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import QObject, pyqtSignal
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from utils.logger import get_logger


class ProcessingState(Enum):
    """処理状態の列挙型"""
    IDLE = "idle"
    PROCESSING = "processing" 
    ERROR_DETECTION = "error_detection"
    PDF_POSTING = "pdf_posting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ApplicationState:
    """アプリケーション状態データクラス"""
    processing_state: ProcessingState = ProcessingState.IDLE
    current_n_codes: List[str] = None
    process_mode: str = "api"
    email_password: Optional[str] = None
    error_detection_active: bool = False
    last_error: Optional[str] = None
    last_update: datetime = None
    
    def __post_init__(self):
        if self.current_n_codes is None:
            self.current_n_codes = []
        if self.last_update is None:
            self.last_update = datetime.now()


class StateManager(QObject):
    """アプリケーション状態管理クラス
    
    責任:
    - アプリケーション全体の状態管理
    - 状態変更の通知
    - 状態の整合性保証
    - 状態履歴の管理
    
    Note: MainWindowから分離された状態管理部分
    """
    
    # シグナル定義
    state_changed = pyqtSignal(str, object)  # state_key, new_value
    processing_state_changed = pyqtSignal(ProcessingState)
    error_occurred = pyqtSignal(str)  # error_message
    config_updated = pyqtSignal(str, object)  # config_key, config_value
    
    def __init__(self):
        """StateManager初期化"""
        super().__init__()
        self.logger = get_logger(__name__)
        
        # アプリケーション状態
        self._app_state = ApplicationState()
        
        # 設定状態
        self._config_state: Dict[str, Any] = {}
        
        # UI状態
        self._ui_state: Dict[str, Any] = {
            "window_geometry": None,
            "splitter_sizes": None,
            "current_tab": 0,
            "dialog_states": {}
        }
        
        # 処理履歴
        self._processing_history: List[Dict[str, Any]] = []
        
        self.logger.info("StateManager initialized")
    
    @property
    def current_state(self) -> ApplicationState:
        """現在のアプリケーション状態を取得"""
        return self._app_state
    
    def set_processing_state(self, is_processing: bool, n_codes: List[str] = None):
        """処理状態を設定
        
        Args:
            is_processing: 処理中フラグ
            n_codes: 処理対象N-codes (処理開始時のみ)
        """
        try:
            old_state = self._app_state.processing_state
            
            if is_processing:
                self._app_state.processing_state = ProcessingState.PROCESSING
                if n_codes:
                    self._app_state.current_n_codes = n_codes
            else:
                self._app_state.processing_state = ProcessingState.IDLE
                self._app_state.current_n_codes = []
            
            self._app_state.last_update = datetime.now()
            
            # 履歴記録
            self._add_to_history("processing_state_changed", {
                "old_state": old_state.value,
                "new_state": self._app_state.processing_state.value,
                "n_codes_count": len(self._app_state.current_n_codes) if n_codes else 0
            })
            
            # シグナル発信
            self.processing_state_changed.emit(self._app_state.processing_state)
            self.state_changed.emit("processing_state", self._app_state.processing_state)
            
            self.logger.info(f"Processing state changed: {old_state.value} → {self._app_state.processing_state.value}")
            
        except Exception as e:
            self.logger.error(f"Processing state設定エラー: {e}", exc_info=True)
            self.error_occurred.emit(f"状態設定エラー: {str(e)}")
    
    def set_error_detection_state(self, is_active: bool):
        """エラー検出状態を設定
        
        Args:
            is_active: エラー検出実行中フラグ
        """
        try:
            old_state = self._app_state.error_detection_active
            self._app_state.error_detection_active = is_active
            
            if is_active:
                self._app_state.processing_state = ProcessingState.ERROR_DETECTION
            else:
                self._app_state.processing_state = ProcessingState.IDLE
            
            self._app_state.last_update = datetime.now()
            
            # 履歴記録
            self._add_to_history("error_detection_state_changed", {
                "old_state": old_state,
                "new_state": is_active
            })
            
            # シグナル発信
            self.state_changed.emit("error_detection_state", is_active)
            self.processing_state_changed.emit(self._app_state.processing_state)
            
            self.logger.info(f"Error detection state changed: {old_state} → {is_active}")
            
        except Exception as e:
            self.logger.error(f"Error detection state設定エラー: {e}", exc_info=True)
            self.error_occurred.emit(f"エラー検出状態設定エラー: {str(e)}")
    
    def set_process_mode(self, mode: str):
        """処理モードを設定
        
        Args:
            mode: 処理モード ('api' | 'traditional' | 'gmail_api')
        """
        try:
            old_mode = self._app_state.process_mode
            self._app_state.process_mode = mode
            self._app_state.last_update = datetime.now()
            
            # 履歴記録
            self._add_to_history("process_mode_changed", {
                "old_mode": old_mode,
                "new_mode": mode
            })
            
            # シグナル発信
            self.state_changed.emit("process_mode", mode)
            
            self.logger.info(f"Process mode changed: {old_mode} → {mode}")
            
        except Exception as e:
            self.logger.error(f"Process mode設定エラー: {e}", exc_info=True)
            self.error_occurred.emit(f"処理モード設定エラー: {str(e)}")
    
    def set_email_password(self, password: Optional[str]):
        """メールパスワードを設定
        
        Args:
            password: メールパスワード (セキュリティ上、実際の値はログに記録しない)
        """
        try:
            self._app_state.email_password = password
            self._app_state.last_update = datetime.now()
            
            # セキュリティ上、パスワードの有無のみ履歴に記録
            self._add_to_history("email_password_changed", {
                "has_password": password is not None
            })
            
            # シグナル発信
            self.state_changed.emit("email_password", password is not None)  # boolean値のみ送信
            
            self.logger.info(f"Email password {'set' if password else 'cleared'}")
            
        except Exception as e:
            self.logger.error(f"Email password設定エラー: {e}", exc_info=True)
            self.error_occurred.emit(f"パスワード設定エラー: {str(e)}")
    
    def set_error_state(self, error_message: str):
        """エラー状態を設定
        
        Args:
            error_message: エラーメッセージ
        """
        try:
            self._app_state.processing_state = ProcessingState.ERROR
            self._app_state.last_error = error_message
            self._app_state.last_update = datetime.now()
            
            # 履歴記録
            self._add_to_history("error_occurred", {
                "error_message": error_message,
                "timestamp": self._app_state.last_update.isoformat()
            })
            
            # シグナル発信
            self.error_occurred.emit(error_message)
            self.processing_state_changed.emit(self._app_state.processing_state)
            
            self.logger.error(f"Application error state set: {error_message}")
            
        except Exception as e:
            self.logger.error(f"Error state設定エラー: {e}", exc_info=True)
    
    def update_config(self, key: str, value: Any):
        """設定を更新
        
        Args:
            key: 設定キー
            value: 設定値
        """
        try:
            old_value = self._config_state.get(key)
            self._config_state[key] = value
            
            # 履歴記録
            self._add_to_history("config_updated", {
                "key": key,
                "old_value": old_value,
                "new_value": value
            })
            
            # シグナル発信
            self.config_updated.emit(key, value)
            self.state_changed.emit(f"config.{key}", value)
            
            self.logger.info(f"Config updated: {key} = {value}")
            
        except Exception as e:
            self.logger.error(f"Config更新エラー: {e}", exc_info=True)
            self.error_occurred.emit(f"設定更新エラー: {str(e)}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """設定値を取得
        
        Args:
            key: 設定キー
            default: デフォルト値
            
        Returns:
            Any: 設定値
        """
        return self._config_state.get(key, default)
    
    def update_ui_state(self, key: str, value: Any):
        """UI状態を更新
        
        Args:
            key: UI状態キー
            value: UI状態値
        """
        try:
            old_value = self._ui_state.get(key)
            self._ui_state[key] = value
            
            # シグナル発信
            self.state_changed.emit(f"ui.{key}", value)
            
            # 詳細ログはUI状態には不要
            
        except Exception as e:
            self.logger.error(f"UI state更新エラー: {e}", exc_info=True)
    
    def get_ui_state(self, key: str, default: Any = None) -> Any:
        """UI状態値を取得
        
        Args:
            key: UI状態キー  
            default: デフォルト値
            
        Returns:
            Any: UI状態値
        """
        return self._ui_state.get(key, default)
    
    def reset_all_states(self):
        """全ての状態をリセット"""
        try:
            # アプリケーション状態リセット
            self._app_state = ApplicationState()
            
            # UI状態は保持（ウィンドウ位置など）
            # 設定状態は保持
            
            # 履歴記録
            self._add_to_history("all_states_reset", {
                "timestamp": datetime.now().isoformat()
            })
            
            # シグナル発信
            self.processing_state_changed.emit(self._app_state.processing_state)
            self.state_changed.emit("reset", True)
            
            self.logger.info("All states reset")
            
        except Exception as e:
            self.logger.error(f"State reset エラー: {e}", exc_info=True)
            self.error_occurred.emit(f"状態リセットエラー: {str(e)}")
    
    def get_processing_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """処理履歴を取得
        
        Args:
            limit: 取得する履歴数の上限
            
        Returns:
            List[Dict[str, Any]]: 処理履歴
        """
        return self._processing_history[-limit:] if self._processing_history else []
    
    def _add_to_history(self, action: str, data: Dict[str, Any]):
        """履歴にアクションを追加
        
        Args:
            action: アクション名
            data: アクションデータ
        """
        try:
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "data": data
            }
            
            self._processing_history.append(history_entry)
            
            # 履歴数制限（メモリ使用量制御）
            if len(self._processing_history) > 1000:
                self._processing_history = self._processing_history[-500:]  # 半分に削減
                
        except Exception as e:
            self.logger.error(f"履歴追加エラー: {e}", exc_info=True)