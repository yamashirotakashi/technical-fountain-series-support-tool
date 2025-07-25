"""繝ｭ繧ｰ陦ｨ遉ｺ繝代ロ繝ｫ繝｢繧ｸ繝･繝ｼ繝ｫ"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat
from datetime import datetime
from pathlib import Path


class LogPanel(QWidget):
    """繝ｭ繧ｰ繧定｡ｨ遉ｺ縺吶ｋ繝代ロ繝ｫ繧ｦ繧｣繧ｸ繧ｧ繝・ヨ"""
    
    def __init__(self, parent=None):
        """
        LogPanel繧貞・譛溷喧
        
        Args:
            parent: 隕ｪ繧ｦ繧｣繧ｸ繧ｧ繝・ヨ
        """
        super().__init__(parent)
        self.auto_scroll = True
        self.setup_ui()
    
    def setup_ui(self):
        """UI繧呈ｧ狗ｯ・""
        layout = QVBoxLayout(self)
        
        # 繝ｭ繧ｰ陦ｨ遉ｺ繧ｨ繝ｪ繧｢
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        
        # 繝懊ち繝ｳ繝ｬ繧､繧｢繧ｦ繝・        button_layout = QHBoxLayout()
        
        # 繧ｯ繝ｪ繧｢繝懊ち繝ｳ
        self.clear_button = QPushButton("繝ｭ繧ｰ繧ｯ繝ｪ繧｢")
        self.clear_button.clicked.connect(self.clear_logs)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        
        # 閾ｪ蜍輔せ繧ｯ繝ｭ繝ｼ繝ｫ繝医げ繝ｫ繝懊ち繝ｳ
        self.auto_scroll_button = QPushButton("閾ｪ蜍輔せ繧ｯ繝ｭ繝ｼ繝ｫ: ON")
        self.auto_scroll_button.setCheckable(True)
        self.auto_scroll_button.setChecked(True)
        self.auto_scroll_button.clicked.connect(self.toggle_auto_scroll)
        self.auto_scroll_button.setStyleSheet("""
            QPushButton {
                background-color: #2d7d2d;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3d8d3d;
            }
            QPushButton:checked {
                background-color: #2d7d2d;
            }
            QPushButton:!checked {
                background-color: #666;
            }
        """)
        
        # 菫晏ｭ倥・繧ｿ繝ｳ
        self.save_button = QPushButton("繝ｭ繧ｰ菫晏ｭ・)
        self.save_button.clicked.connect(self.save_logs)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2d5d7d;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3d6d8d;
            }
        """)
        
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.auto_scroll_button)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        
        layout.addWidget(self.log_display)
        layout.addLayout(button_layout)
    
    @pyqtSlot(str, str)
    def append_log(self, message: str, level: str = "INFO"):
        """
        繝ｭ繧ｰ繝｡繝・そ繝ｼ繧ｸ繧定ｿｽ蜉
        
        Args:
            message: 繝ｭ繧ｰ繝｡繝・そ繝ｼ繧ｸ
            level: 繝ｭ繧ｰ繝ｬ繝吶Ν
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 繧ｫ繝ｼ繧ｽ繝ｫ繧貞叙蠕・        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # 繝ｬ繝吶Ν縺ｫ蠢懊§縺溯牡繧定ｨｭ螳・        level_colors = {
            "DEBUG": QColor("#808080"),
            "INFO": QColor("#ffffff"),
            "WARNING": QColor("#ffcc00"),
            "ERROR": QColor("#ff4444"),
            "CRITICAL": QColor("#ff0000")
        }
        
        # 繧ｿ繧､繝繧ｹ繧ｿ繝ｳ繝励ｒ霑ｽ蜉
        timestamp_format = QTextCharFormat()
        timestamp_format.setForeground(QColor("#888888"))
        cursor.setCharFormat(timestamp_format)
        cursor.insertText(f"[{timestamp}] ")
        
        # 繝ｬ繝吶Ν繧定ｿｽ蜉
        level_format = QTextCharFormat()
        level_format.setForeground(level_colors.get(level, QColor("#ffffff")))
        cursor.setCharFormat(level_format)
        cursor.insertText(f"{level}: ")
        
        # 繝｡繝・そ繝ｼ繧ｸ繧定ｿｽ蜉
        message_format = QTextCharFormat()
        message_format.setForeground(QColor("#ffffff"))
        cursor.setCharFormat(message_format)
        cursor.insertText(f"{message}\n")
        
        # 閾ｪ蜍輔せ繧ｯ繝ｭ繝ｼ繝ｫ
        if self.auto_scroll:
            self.log_display.setTextCursor(cursor)
            self.log_display.ensureCursorVisible()
    
    def clear_logs(self):
        """繝ｭ繧ｰ繧偵け繝ｪ繧｢"""
        self.log_display.clear()
    
    def toggle_auto_scroll(self):
        """閾ｪ蜍輔せ繧ｯ繝ｭ繝ｼ繝ｫ縺ｮ蛻・ｊ譖ｿ縺・""
        self.auto_scroll = self.auto_scroll_button.isChecked()
        text = "閾ｪ蜍輔せ繧ｯ繝ｭ繝ｼ繝ｫ: ON" if self.auto_scroll else "閾ｪ蜍輔せ繧ｯ繝ｭ繝ｼ繝ｫ: OFF"
        self.auto_scroll_button.setText(text)
    
    def save_logs(self):
        """繝ｭ繧ｰ繧偵ヵ繧｡繧､繝ｫ縺ｫ菫晏ｭ・""
        from PyQt6.QtWidgets import QFileDialog
        
        # 繝輔ぃ繧､繝ｫ菫晏ｭ倥ム繧､繧｢繝ｭ繧ｰ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"technical_fountain_log_{timestamp}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "繝ｭ繧ｰ繝輔ぃ繧､繝ｫ縺ｮ菫晏ｭ・,
            default_filename,
            "繝・く繧ｹ繝医ヵ繧｡繧､繝ｫ (*.txt);;縺吶∋縺ｦ縺ｮ繝輔ぃ繧､繝ｫ (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_display.toPlainText())
                self.append_log(f"繝ｭ繧ｰ繧剃ｿ晏ｭ倥＠縺ｾ縺励◆: {file_path}", "INFO")
            except Exception as e:
                self.append_log(f"繝ｭ繧ｰ縺ｮ菫晏ｭ倥↓螟ｱ謨励＠縺ｾ縺励◆: {e}", "ERROR")