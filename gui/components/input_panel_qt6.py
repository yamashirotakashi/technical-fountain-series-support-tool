"""Input panel module"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QGroupBox)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from utils.validators_qt6 import Validators


class InputPanel(QWidget):
    """N-code input panel widget"""
    
    # Custom signals
    processing_requested = pyqtSignal(list)  # Send N-code list
    settings_requested = pyqtSignal()  # Settings button clicked
    # preflight_requested = pyqtSignal()  # Pre-flight Check button clicked (削除)
    error_check_requested = pyqtSignal(list)  # Error file detection requested
    
    def __init__(self, parent=None):
        """
        Initialize InputPanel
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        
        # Group box
        group_box = QGroupBox("Nコード入力")
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        group_layout = QVBoxLayout(group_box)
        
        # Description label
        description_label = QLabel(
            "処理するNコードを入力してください。\n"
            "複数のコードはカンマ (,)、タブ、スペース、または改行で区切ることができます。\n"
            "例: N00001, N00002 または N00001[Tab]N00002 または1行に1つ"
        )
        description_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        
        # Input area
        self.n_code_input = QTextEdit()
        self.n_code_input.setMaximumHeight(100)
        self.n_code_input.setPlaceholderText("N00001, N00002, N00003...")
        self.n_code_input.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12pt;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTextEdit:focus {
                border-color: #4CAF50;
            }
        """)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Process button
        self.process_button = QPushButton("処理開始")
        self.process_button.clicked.connect(self.on_process_clicked)
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        # Clear button
        self.clear_button = QPushButton("クリア")
        self.clear_button.clicked.connect(self.clear_input)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c01005;
            }
        """)
        
        # Settings button (処理方式選択)
        self.settings_button = QPushButton("処理方式")
        self.settings_button.clicked.connect(self.on_settings_clicked)
        self.settings_button.setToolTip("API方式、メール方式、Gmail API方式から選択")
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0960aa;
            }
        """)
        
        # Pre-flight Check button (削除)
        
        # Error file detection button
        self.error_check_button = QPushButton("エラーファイル検知")
        self.error_check_button.clicked.connect(self.on_error_check_clicked)
        self.error_check_button.setToolTip("組版エラー後の原因ファイルを特定します")
        self.error_check_button.setStyleSheet("""
            QPushButton {
                background-color: #E91E63;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #C2185B;
            }
            QPushButton:pressed {
                background-color: #AD1457;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        # Add buttons
        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addWidget(self.error_check_button)
        # button_layout.addWidget(self.preflight_button)  # 削除
        button_layout.addStretch()
        
        # Add to group layout
        group_layout.addWidget(description_label)
        group_layout.addWidget(self.n_code_input)
        group_layout.addLayout(button_layout)
        
        # Add to main layout
        layout.addWidget(group_box)
        layout.addStretch()
    
    def get_n_codes(self) -> list:
        """
        Get list of entered N-codes
        
        Returns:
            List of valid N-codes
        """
        text = self.n_code_input.toPlainText()
        valid_codes, _ = Validators.validate_n_codes(text)
        return valid_codes
    
    def validate_input(self) -> bool:
        """
        Validate input
        
        Returns:
            True if validation succeeds
        """
        text = self.n_code_input.toPlainText()
        valid_codes, errors = Validators.validate_n_codes(text)
        
        if not text.strip():
            self.show_error("Please enter N-codes.")
            return False
        
        if errors:
            error_message = "Input errors:\n" + "\n".join(errors)
            self.show_error(error_message)
            return False
        
        if not valid_codes:
            self.show_error("No valid N-codes entered.")
            return False
        
        return True
    
    def on_process_clicked(self):
        """Handler for process button click"""
        if self.validate_input():
            n_codes = self.get_n_codes()
            self.processing_requested.emit(n_codes)
    
    def clear_input(self):
        """Clear input"""
        self.n_code_input.clear()
    
    def on_settings_clicked(self):
        """Handler for settings button click"""
        self.settings_requested.emit()
    
    # Pre-flight Check handler (削除)
    
    def on_error_check_clicked(self):
        """Handler for error file detection button click"""
        if self.validate_input():
            n_codes = self.get_n_codes()
            self.error_check_requested.emit(n_codes)
    
    def show_error(self, message: str):
        """Show error message"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Input Error", message)
    
    def set_enabled(self, enabled: bool):
        """Set panel enabled/disabled"""
        self.process_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)
        self.settings_button.setEnabled(enabled)
        # self.preflight_button.setEnabled(enabled)  # 削除
        self.error_check_button.setEnabled(enabled)
        self.n_code_input.setEnabled(enabled)