from __future__ import annotations
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
            
            if self.process_mode == ProcessModeDialog.MODE_API:
                self.api_processor = ApiProcessor()
                self.api_processor.log_message.connect(self.log_message.emit)
                self.api_processor.status_updated.connect(self.status_updated.emit)
                self.api_processor.progress_updated.connect(self.progress_updated.emit)
                self.workflow_processor.set_api_processor(self.api_processor)
            
            success = self.workflow_processor.process(self.n_codes)
            
            if success:
                self.log_message.emit("SUCCESS", "Process completed successfully")
            else:
                self.log_message.emit("ERROR", "Process failed")
        except Exception as e:
            self.logger.error(f"Worker error: {e}", exc_info=True)
            self.log_message.emit("ERROR", f"Error: {str(e)}")
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
        self.setWindowTitle("Technical Fountain Series Support Tool")
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
        file_menu = menubar.addMenu("File(&F)")
        
        exit_action = QAction("Exit(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools(&T)")
        
        clear_log_action = QAction("Clear Log(&C)", self)
        clear_log_action.triggered.connect(self.log_panel.clear_logs)
        tools_menu.addAction(clear_log_action)
        
        tools_menu.addSeparator()
        
        repo_settings_action = QAction("Repository Settings(&R)", self)
        repo_settings_action.triggered.connect(self.show_repository_settings)
        tools_menu.addAction(repo_settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help(&H)")
        
        about_action = QAction("About(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_statusbar(self):
        self.statusBar().showMessage("Ready")
    
    def connect_signals(self):
        self.input_panel.processing_requested.connect(self.start_processing)
        self.input_panel.settings_requested.connect(self.show_repository_settings)
        self.progress_panel.cancel_requested.connect(self.cancel_processing)
    
    @pyqtSlot(list, int)
    def start_processing(self, n_codes, process_mode):
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "Warning", "Processing is already in progress")
            return
        
        self.process_mode = process_mode
        
        if process_mode == ProcessModeDialog.MODE_TRADITIONAL:
            email, ok = QInputDialog.getText(
                self, 
                "Email Password",
                "Enter Gmail app password:",
                QLineEdit.EchoMode.Password
            )
            if not ok or not email:
                return
        else:
            email = None
        
        self.input_panel.set_enabled(False)
        self.progress_panel.reset_progress()
        self.log_panel.add_log("INFO", "Starting process...")
        
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
            self.log_panel.add_log("WARNING", "Process cancelled")
            self.processing_finished()
    
    @pyqtSlot()
    def processing_finished(self):
        self.input_panel.set_enabled(True)
        self.progress_panel.set_cancel_enabled(False)
        self.statusBar().showMessage("Ready")
    
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
        dialog = FolderSelectorDialog(self, repo_path, repo_name, default_folder)
        if dialog.exec():
            selected_folder = dialog.get_selected_folder()
            if self.worker_thread and hasattr(self.worker_thread.workflow_processor, 'folder_selection_callback'):
                self.worker_thread.workflow_processor.folder_selection_callback(selected_folder)
        else:
            if self.worker_thread and hasattr(self.worker_thread.workflow_processor, 'folder_selection_callback'):
                self.worker_thread.workflow_processor.folder_selection_callback(None)
    
    @pyqtSlot(str, list, object)
    def handle_file_placement_confirmation(self, honbun_folder_path, file_list, callback):
        dialog = SimpleFileSelectorDialog(self, honbun_folder_path, file_list)
        if dialog.exec():
            callback(True)
        else:
            callback(False)
    
    @pyqtSlot(list, str)
    def handle_warning_dialog(self, messages, result_type):
        dialog = WarningDialog(self, messages, result_type)
        dialog.exec()
    
    def show_repository_settings(self):
        from gui.repository_settings_dialog import RepositorySettingsDialog
        dialog = RepositorySettingsDialog(self)
        dialog.exec()
    
    def show_about(self):
        QMessageBox.about(self, "About",
                         "Technical Fountain Series Support Tool\n\n"
                         "Version 1.0.0\n\n"
                         "Automates the production process of Technical Fountain Series")
    
    def closeEvent(self, event):
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(self, "Confirm Exit",
                                       "Processing is in progress. Do you want to exit?",
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