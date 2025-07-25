"""Main window module"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QMenuBar, QStatusBar, QMessageBox,
                             QInputDialog, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal, QCoreApplication
from PyQt6.QtGui import QIcon, QAction

from gui.components.input_panel_qt6 import InputPanel
from gui.components.log_panel_qt6 import LogPanel
from gui.components.progress_bar_qt6 import ProgressPanel
from gui.dialogs import FolderSelectorDialog
from gui.dialogs.simple_file_selector_dialog import SimpleFileSelectorDialog
from gui.dialogs.process_mode_dialog import ProcessModeDialog
from gui.dialogs.warning_dialog import WarningDialog
from core.workflow_processor import WorkflowProcessor
from core.api_processor import ApiProcessor
from utils.logger import get_logger
from pathlib import Path


class ProcessWorker(QThread):
    progress_updated = pyqtSignal(int)
    log_message = pyqtSignal(str, str)
    status_updated = pyqtSignal(str)
    confirmation_needed = pyqtSignal(str, str)
    folder_selection_needed = pyqtSignal(object, str, object)  # repo_path, repo_name, default_folder
    file_placement_confirmation_needed = pyqtSignal(str, list, object)  # honbun_folder_path, file_list, callback
    warning_dialog_needed = pyqtSignal(list, str)  # messages, result_type
    finished = pyqtSignal()
    
    def __init__(self, n_codes, email_password=None, process_mode="traditional"):
        super().__init__()
        self.n_codes = n_codes
        self.email_password = email_password
        self.process_mode = process_mode
        self.workflow_processor = None
        self.api_processor = None
        self.logger = get_logger(__name__)
    
    def run(self):
        try:
            # デバッグ用ログ
            print(f"[DEBUG] ProcessWorker.run: process_mode={self.process_mode}")
            print(f"[DEBUG] ProcessWorker.run: email_password={'set' if self.email_password else 'not set'}")
            
            self.workflow_processor = WorkflowProcessor(
                email_password=self.email_password,
                process_mode=self.process_mode
            )
            
            self.workflow_processor.log_message.connect(self.log_message.emit)
            self.workflow_processor.status_updated.connect(self.status_updated.emit)
            self.workflow_processor.progress_updated.connect(self.progress_updated.emit)
            self.workflow_processor.confirmation_needed.connect(self.confirmation_needed.emit)
            self.workflow_processor.folder_selection_needed.connect(self.folder_selection_needed.emit)
            self.workflow_processor.file_placement_confirmation_needed.connect(self.file_placement_confirmation_needed.emit)
            self.workflow_processor.warning_dialog_needed.connect(self.warning_dialog_needed.emit)
            
            # API processorは WorkflowProcessor内で自動的に管理される
            
            self.workflow_processor.process_n_codes(self.n_codes)
            success = True
            
            if success:
                self.log_message.emit("SUCCESS", "処理が正常に完了しました")
            else:
                self.log_message.emit("ERROR", "処理が失敗しました")
        except Exception as e:
            self.logger.error(f"Worker error: {e}", exc_info=True)
            self.log_message.emit("ERROR", f"エラー: {str(e)}")
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.process_mode = ProcessModeDialog.MODE_TRADITIONAL
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.connect_signals()
    
    def setup_ui(self):
        self.setWindowTitle("技術の泉シリーズ制作支援ツール")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        self.input_panel = InputPanel()
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        self.log_panel = LogPanel()
        self.progress_panel = ProgressPanel()
        
        splitter.addWidget(self.log_panel)
        splitter.setStretchFactor(0, 1)
        
        main_layout.addWidget(self.input_panel)
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.progress_panel)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("ファイル(&F)")
        
        exit_action = QAction("終了(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("ツール(&T)")
        
        clear_log_action = QAction("ログをクリア(&C)", self)
        clear_log_action.triggered.connect(self.log_panel.clear_logs)
        tools_menu.addAction(clear_log_action)
        
        tools_menu.addSeparator()
        
        repo_settings_action = QAction("リポジトリ設定(&R)", self)
        repo_settings_action.triggered.connect(self.show_repository_settings)
        tools_menu.addAction(repo_settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("ヘルプ(&H)")
        
        about_action = QAction("このアプリケーションについて(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_statusbar(self):
        self.statusBar().showMessage("準備完了")
    
    def connect_signals(self):
        self.input_panel.processing_requested.connect(self.start_processing)
        self.input_panel.settings_requested.connect(self.show_repository_settings)
        self.progress_panel.cancel_requested.connect(self.cancel_processing)
    
    @pyqtSlot(list, str)
    def start_processing(self, n_codes, process_mode):
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "警告", "処理が既に実行中です")
            return
        
        # デバッグ用ログ
        print(f"[DEBUG] start_processing: process_mode={process_mode}, type={type(process_mode)}")
        print(f"[DEBUG] MODE_API={ProcessModeDialog.MODE_API}, MODE_TRADITIONAL={ProcessModeDialog.MODE_TRADITIONAL}")
        
        self.process_mode = process_mode
        
        if process_mode == ProcessModeDialog.MODE_TRADITIONAL:
            email, ok = QInputDialog.getText(
                self, 
                "メールパスワード",
                "Gmailアプリパスワードを入力してください:",
                QLineEdit.EchoMode.Password
            )
            if not ok or not email:
                return
        else:
            email = None
        
        self.input_panel.set_enabled(False)
        self.progress_panel.reset_progress()
        self.log_panel.add_log("INFO", "処理を開始しています...")
        
        self.worker_thread = ProcessWorker(n_codes, email, process_mode)
        self.worker_thread.log_message.connect(self.log_panel.add_log)
        self.worker_thread.status_updated.connect(self.statusBar().showMessage)
        self.worker_thread.progress_updated.connect(self.progress_panel.update_progress)
        self.worker_thread.confirmation_needed.connect(self.handle_confirmation)
        self.worker_thread.folder_selection_needed.connect(self.handle_folder_selection)
        self.worker_thread.file_placement_confirmation_needed.connect(self.handle_file_placement_confirmation)
        self.worker_thread.warning_dialog_needed.connect(self.handle_warning_dialog)
        self.worker_thread.finished.connect(self.processing_finished)
        
        self.worker_thread.start()
    
    @pyqtSlot()
    def cancel_processing(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
            self.log_panel.add_log("WARNING", "処理がキャンセルされました")
            self.processing_finished()
    
    @pyqtSlot()
    def processing_finished(self):
        self.input_panel.set_enabled(True)
        self.progress_panel.set_cancel_enabled(False)
        self.statusBar().showMessage("準備完了")
    
    @pyqtSlot(str, str)
    def handle_confirmation(self, title, message):
        reply = QMessageBox.question(self, title, message,
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        result = reply == QMessageBox.StandardButton.Yes
        if self.worker_thread and hasattr(self.worker_thread.workflow_processor, 'confirmation_callback'):
            self.worker_thread.workflow_processor.confirmation_callback(result)
    
    @pyqtSlot(object, str, object)
    def handle_folder_selection(self, repo_path, repo_name, default_folder):
        # FolderSelectorDialogの引数順序: repo_path, repo_name, default_folder, parent
        dialog = FolderSelectorDialog(repo_path, repo_name, default_folder, self)
        if dialog.exec():
            selected_folder = dialog.selected_folder
            if self.worker_thread and self.worker_thread.workflow_processor:
                self.worker_thread.workflow_processor.set_selected_work_folder(str(selected_folder))
        else:
            if self.worker_thread and self.worker_thread.workflow_processor:
                self.worker_thread.workflow_processor.set_selected_work_folder(None)
    
    @pyqtSlot(str, list, object)
    def handle_file_placement_confirmation(self, honbun_folder_path, file_list, callback):
        dialog = SimpleFileSelectorDialog(file_list, self)
        if dialog.exec():
            selected_files = dialog.get_selected_files()
            callback(selected_files)
        else:
            callback([])
    
    @pyqtSlot(list, str)
    def handle_warning_dialog(self, messages, result_type):
        dialog = WarningDialog(self, messages, result_type)
        dialog.exec()
    
    def show_repository_settings(self):
        from gui.repository_settings_dialog import RepositorySettingsDialog
        dialog = RepositorySettingsDialog(self)
        dialog.exec()
    
    def show_about(self):
        QMessageBox.about(self, "このアプリケーションについて",
                         "技術の泉シリーズ制作支援ツール\n\n"
                         "バージョン 1.0.0\n\n"
                         "技術の泉シリーズの制作プロセスを自動化します")
    
    def closeEvent(self, event):
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(self, "終了確認",
                                       "処理が実行中です。終了しますか？",
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.worker_thread.terminate()
                self.worker_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()