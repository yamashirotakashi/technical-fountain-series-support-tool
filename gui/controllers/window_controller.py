"""
Window Controller - UI制御専用コントローラー

Phase 3-1: God Object解消の一環として、MainWindowからUI制御ロジックを分離。
SOLID原則のSingle Responsibilityに準拠し、UIの表示・制御のみに責任を限定。
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict, Any, List
from PyQt6.QtWidgets import (QMainWindow, QMessageBox, QInputDialog, QLineEdit, 
                           QDialog, QDialogButtonBox, QVBoxLayout, QLabel)
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QIcon

from gui.dialogs import FolderSelectorDialog
from gui.dialogs.simple_file_selector_dialog import SimpleFileSelectorDialog
from gui.dialogs.process_mode_dialog import ProcessModeDialog
from gui.dialogs.warning_dialog import WarningDialog
from gui.comprehensive_settings_dialog import ComprehensiveSettingsDialog
from gui.repository_settings_dialog import RepositorySettingsDialog
from utils.logger import get_logger

if TYPE_CHECKING:
    from gui.main_window import MainWindow
    from gui.managers.state_manager import StateManager


class WindowController(QObject):
    """UI制御専用コントローラー
    
    責任:
    - ダイアログ表示管理
    - ユーザーインタラクション処理
    - UI状態の可視化
    - メニュー・ツールバー制御
    
    Note: MainWindowから分離されたUI制御部分
    """
    
    # シグナル定義
    processing_requested = pyqtSignal(list)  # n_codes
    error_detection_requested = pyqtSignal(list)  # n_codes
    pdf_post_requested = pyqtSignal(str)  # n_code
    settings_requested = pyqtSignal(str)  # settings_type
    about_requested = pyqtSignal()
    hardcoding_scan_requested = pyqtSignal()
    
    def __init__(self, main_window: 'MainWindow', state_manager: 'StateManager'):
        """WindowController初期化
        
        Args:
            main_window: メインウィンドウインスタンス
            state_manager: 状態管理マネージャー
        """
        super().__init__()
        self.main_window = main_window
        self.state_manager = state_manager
        self.logger = get_logger(__name__)
        
        # ダイアログインスタンス保持
        self._dialogs: Dict[str, QDialog] = {}
        
        # UI状態監視
        self.state_manager.state_changed.connect(self._on_state_changed)
        self.state_manager.processing_state_changed.connect(self._on_processing_state_changed)
        
        self.logger.info("WindowController initialized")
    
    def show_confirmation_dialog(self, title: str, message: str) -> bool:
        """確認ダイアログを表示
        
        Args:
            title: ダイアログタイトル
            message: 確認メッセージ
            
        Returns:
            bool: ユーザーの選択 (True: OK, False: Cancel)
        """
        try:
            reply = QMessageBox.question(
                self.main_window,
                title,
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            result = reply == QMessageBox.StandardButton.Yes
            self.logger.info(f"Confirmation dialog result: {result} for '{title}'")
            return result
            
        except Exception as e:
            self.logger.error(f"Confirmation dialog error: {e}", exc_info=True)
            return False
    
    def show_about_dialog(self):
        """About ダイアログを表示"""
        try:
            if 'about' not in self._dialogs:
                about_dialog = QDialog(self.main_window)
                about_dialog.setWindowTitle("Technical Fountain Series Support Tool について")
                about_dialog.setModal(True)
                about_dialog.resize(400, 200)
                
                layout = QVBoxLayout()
                layout.addWidget(QLabel("Technical Fountain Series Support Tool"))
                layout.addWidget(QLabel("Version: 1.8 (Phase 3 Architecture)"))
                layout.addWidget(QLabel("技術の泉シリーズ制作支援ツール"))
                layout.addWidget(QLabel(""))
                layout.addWidget(QLabel("Phase 3: Complete Architecture Refactoring"))
                layout.addWidget(QLabel("- SOLID原則準拠"))
                layout.addWidget(QLabel("- Dependency Injection実装"))
                layout.addWidget(QLabel("- God Object解消完了"))
                
                buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
                buttons.accepted.connect(about_dialog.accept)
                layout.addWidget(buttons)
                
                about_dialog.setLayout(layout)
                self._dialogs['about'] = about_dialog
            
            self._dialogs['about'].show()
            self.logger.info("About dialog displayed")
            
        except Exception as e:
            self.logger.error(f"About dialog error: {e}", exc_info=True)
    
    def show_process_mode_dialog(self) -> Optional[str]:
        """処理モード選択ダイアログを表示
        
        Returns:
            Optional[str]: 選択された処理モード (None: キャンセル)
        """
        try:
            if 'process_mode' not in self._dialogs:
                self._dialogs['process_mode'] = ProcessModeDialog(self.main_window)
            
            dialog = self._dialogs['process_mode']
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_mode = dialog.get_selected_mode()
                self.logger.info(f"Process mode selected: {selected_mode}")
                return selected_mode
            
            return None
            
        except Exception as e:
            self.logger.error(f"Process mode dialog error: {e}", exc_info=True)
            return None
    
    def show_comprehensive_settings_dialog(self):
        """包括的設定ダイアログを表示"""
        try:
            if 'comprehensive_settings' not in self._dialogs:
                self._dialogs['comprehensive_settings'] = ComprehensiveSettingsDialog(self.main_window)
                # 設定変更シグナル接続
                self._dialogs['comprehensive_settings'].config_changed.connect(self._on_config_changed)
                self._dialogs['comprehensive_settings'].settings_updated.connect(self._on_settings_updated)
            
            self._dialogs['comprehensive_settings'].show()
            self.logger.info("Comprehensive settings dialog displayed")
            
        except Exception as e:
            self.logger.error(f"Comprehensive settings dialog error: {e}", exc_info=True)
    
    def show_repository_settings_dialog(self):
        """リポジトリ設定ダイアログを表示"""
        try:
            if 'repository_settings' not in self._dialogs:
                self._dialogs['repository_settings'] = RepositorySettingsDialog(self.main_window)
            
            self._dialogs['repository_settings'].show()
            self.logger.info("Repository settings dialog displayed")
            
        except Exception as e:
            self.logger.error(f"Repository settings dialog error: {e}", exc_info=True)
    
    def show_hardcoding_scan_dialog(self):
        """ハードコーディングスキャンダイアログを表示"""
        try:
            # ハードコーディングスキャン要求シグナル発信
            self.hardcoding_scan_requested.emit()
            self.logger.info("Hardcoding scan requested")
            
        except Exception as e:
            self.logger.error(f"Hardcoding scan dialog error: {e}", exc_info=True)
    
    def show_folder_selection_dialog(self, repo_path: str, repo_name: str, 
                                   default_folder: str) -> Optional[str]:
        """フォルダー選択ダイアログを表示
        
        Args:
            repo_path: リポジトリパス
            repo_name: リポジトリ名
            default_folder: デフォルトフォルダー
            
        Returns:
            Optional[str]: 選択されたフォルダーパス (None: キャンセル)
        """
        try:
            dialog = FolderSelectorDialog(repo_path, repo_name, default_folder, self.main_window)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_folder = dialog.get_selected_folder()
                save_settings = dialog.should_save_settings()
                
                self.logger.info(f"Folder selected: {selected_folder}, save_settings: {save_settings}")
                return selected_folder
            
            return None
            
        except Exception as e:
            self.logger.error(f"Folder selection dialog error: {e}", exc_info=True)
            return None
    
    def show_file_placement_confirmation_dialog(self, honbun_folder_path: str, 
                                               file_list: List[str]) -> bool:
        """ファイル配置確認ダイアログを表示
        
        Args:
            honbun_folder_path: 本文フォルダーパス
            file_list: ファイルリスト
            
        Returns:
            bool: ユーザーの選択 (True: OK, False: Cancel)
        """
        try:
            files_text = "\n".join([f"・{file}" for file in file_list])
            message = f"以下のファイルを次のフォルダに配置します：\n\n{honbun_folder_path}\n\n{files_text}\n\n続行しますか？"
            
            return self.show_confirmation_dialog("ファイル配置確認", message)
            
        except Exception as e:
            self.logger.error(f"File placement confirmation dialog error: {e}", exc_info=True)
            return False
    
    def show_warning_dialog(self, messages: List[str], result_type: str):
        """警告ダイアログを表示
        
        Args:
            messages: 警告メッセージリスト
            result_type: 結果タイプ
        """
        try:
            dialog = WarningDialog(messages, result_type, self.main_window)
            dialog.show()
            
            self.logger.info(f"Warning dialog displayed: {len(messages)} messages, type: {result_type}")
            
        except Exception as e:
            self.logger.error(f"Warning dialog error: {e}", exc_info=True)
    
    def show_error_file_selection_dialog(self, file_list: List[str]) -> List[str]:
        """エラーファイル選択ダイアログを表示
        
        Args:
            file_list: エラーファイルリスト
            
        Returns:
            List[str]: 選択されたファイルリスト
        """
        try:
            dialog = SimpleFileSelectorDialog(file_list, "エラーファイルを選択", self.main_window)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_files = dialog.get_selected_files()
                self.logger.info(f"Error files selected: {len(selected_files)} files")
                return selected_files
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error file selection dialog error: {e}", exc_info=True)
            return []
    
    def update_window_title(self, title: str):
        """ウィンドウタイトルを更新
        
        Args:
            title: 新しいタイトル
        """
        try:
            self.main_window.setWindowTitle(title)
            
        except Exception as e:
            self.logger.error(f"Window title update error: {e}", exc_info=True)
    
    def update_status_bar(self, message: str):
        """ステータスバーを更新
        
        Args:
            message: ステータスメッセージ
        """
        try:
            self.main_window.statusBar().showMessage(message)
            
        except Exception as e:
            self.logger.error(f"Status bar update error: {e}", exc_info=True)
    
    def enable_ui_elements(self, enabled: bool):
        """UI要素の有効/無効を切り替え
        
        Args:
            enabled: 有効化フラグ
        """
        try:
            # メインのUI要素を有効/無効化
            if hasattr(self.main_window, 'input_panel'):
                self.main_window.input_panel.setEnabled(enabled)
            
            # メニューアクションの有効/無効化
            if hasattr(self.main_window, 'process_action'):
                self.main_window.process_action.setEnabled(enabled)
            
            self.logger.debug(f"UI elements {'enabled' if enabled else 'disabled'}")
            
        except Exception as e:
            self.logger.error(f"UI elements enable/disable error: {e}", exc_info=True)
    
    @pyqtSlot(str, object)
    def _on_state_changed(self, state_key: str, value: Any):
        """状態変更ハンドラー
        
        Args:
            state_key: 状態キー
            value: 新しい値
        """
        try:
            # UI状態の反映
            if state_key == "processing_state":
                from gui.managers.state_manager import ProcessingState
                is_processing = value in [ProcessingState.PROCESSING, ProcessingState.ERROR_DETECTION]
                self.enable_ui_elements(not is_processing)
                
                # ウィンドウタイトル更新
                if is_processing:
                    self.update_window_title("Technical Fountain Series Support Tool - 処理中...")
                else:
                    self.update_window_title("Technical Fountain Series Support Tool")
                    
        except Exception as e:
            self.logger.error(f"State change handler error: {e}", exc_info=True)
    
    @pyqtSlot(object)
    def _on_processing_state_changed(self, processing_state):
        """処理状態変更ハンドラー
        
        Args:
            processing_state: 新しい処理状態
        """
        try:
            from gui.managers.state_manager import ProcessingState
            
            # ステータスバー更新
            status_messages = {
                ProcessingState.IDLE: "待機中",
                ProcessingState.PROCESSING: "処理実行中...",
                ProcessingState.ERROR_DETECTION: "エラー検出実行中...",
                ProcessingState.PDF_POSTING: "PDF投稿実行中...",
                ProcessingState.COMPLETED: "処理完了",
                ProcessingState.ERROR: "エラーが発生しました"
            }
            
            message = status_messages.get(processing_state, "不明な状態")
            self.update_status_bar(message)
            
        except Exception as e:
            self.logger.error(f"Processing state change handler error: {e}", exc_info=True)
    
    @pyqtSlot(str, object)
    def _on_config_changed(self, key_path: str, value: Any):
        """設定変更ハンドラー
        
        Args:
            key_path: 設定キーパス
            value: 新しい値
        """
        try:
            # 状態管理に設定変更を通知
            self.state_manager.update_config(key_path, value)
            self.logger.info(f"Config changed via UI: {key_path} = {value}")
            
        except Exception as e:
            self.logger.error(f"Config change handler error: {e}", exc_info=True)
    
    @pyqtSlot()
    def _on_settings_updated(self):
        """設定更新完了ハンドラー"""
        try:
            self.update_status_bar("設定が更新されました")
            self.logger.info("Settings updated via UI")
            
        except Exception as e:
            self.logger.error(f"Settings update handler error: {e}", exc_info=True)
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        try:
            # ダイアログを閉じる
            for dialog_name, dialog in self._dialogs.items():
                if dialog and dialog.isVisible():
                    dialog.close()
            
            self._dialogs.clear()
            self.logger.info("WindowController cleanup completed")
            
        except Exception as e:
            self.logger.error(f"WindowController cleanup error: {e}", exc_info=True)