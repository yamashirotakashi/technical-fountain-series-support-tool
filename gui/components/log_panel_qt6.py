"""Log panel module"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QGroupBox,
                             QPushButton, QHBoxLayout)
from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
from datetime import datetime


class LogPanel(QWidget):
    """Log display panel widget"""
    
    def __init__(self, parent=None):
        """
        Initialize LogPanel
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        
        # Group box
        group_box = QGroupBox("処理ログ")
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
        
        # Log display area
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Clear button
        self.clear_button = QPushButton("Clear Log")
        self.clear_button.clicked.connect(self.clear_logs)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                font-weight: bold;
                padding: 6px 15px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:pressed {
                background-color: #cc7a00;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        
        # Add to group layout
        group_layout.addWidget(self.log_display)
        group_layout.addLayout(button_layout)
        
        # Add to main layout
        layout.addWidget(group_box)
    
    @pyqtSlot(str, str)
    def add_log(self, level: str, message: str):
        """
        Add log message
        
        Args:
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
            message: Log message
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Set cursor to end
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_display.setTextCursor(cursor)
        
        # Add timestamp
        time_format = QTextCharFormat()
        time_format.setForeground(QColor("#666666"))
        cursor.insertText(f"[{timestamp}] ", time_format)
        
        # Add level with color
        level_format = QTextCharFormat()
        level_format.setFontWeight(QFont.Weight.Bold)
        
        if level == "INFO":
            level_format.setForeground(QColor("#2196F3"))
        elif level == "WARNING":
            level_format.setForeground(QColor("#ff9800"))
        elif level == "ERROR":
            level_format.setForeground(QColor("#f44336"))
        elif level == "SUCCESS":
            level_format.setForeground(QColor("#4CAF50"))
        else:
            level_format.setForeground(QColor("#666666"))
        
        cursor.insertText(f"[{level}] ", level_format)
        
        # Add message
        message_format = QTextCharFormat()
        message_format.setForeground(QColor("#333333"))
        cursor.insertText(f"{message}\n", message_format)
        
        # Scroll to bottom
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )
    
    # Alias for compatibility
    append_log = add_log
    
    def clear_logs(self):
        """Clear all logs"""
        self.log_display.clear()
        self.add_log("INFO", "Log cleared")