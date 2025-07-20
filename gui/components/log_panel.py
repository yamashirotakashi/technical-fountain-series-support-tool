"""ログ表示パネルモジュール"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat
from datetime import datetime
from pathlib import Path


class LogPanel(QWidget):
    """ログを表示するパネルウィジェット"""
    
    def __init__(self, parent=None):
        """
        LogPanelを初期化
        
        Args:
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self.auto_scroll = True
        self.setup_ui()
    
    def setup_ui(self):
        """UIを構築"""
        layout = QVBoxLayout(self)
        
        # ログ表示エリア
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
        
        # ボタンレイアウト
        button_layout = QHBoxLayout()
        
        # クリアボタン
        self.clear_button = QPushButton("ログクリア")
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
        
        # 自動スクロールトグルボタン
        self.auto_scroll_button = QPushButton("自動スクロール: ON")
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
        
        # 保存ボタン
        self.save_button = QPushButton("ログ保存")
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
        ログメッセージを追加
        
        Args:
            message: ログメッセージ
            level: ログレベル
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # カーソルを取得
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # レベルに応じた色を設定
        level_colors = {
            "DEBUG": QColor("#808080"),
            "INFO": QColor("#ffffff"),
            "WARNING": QColor("#ffcc00"),
            "ERROR": QColor("#ff4444"),
            "CRITICAL": QColor("#ff0000")
        }
        
        # タイムスタンプを追加
        timestamp_format = QTextCharFormat()
        timestamp_format.setForeground(QColor("#888888"))
        cursor.setCharFormat(timestamp_format)
        cursor.insertText(f"[{timestamp}] ")
        
        # レベルを追加
        level_format = QTextCharFormat()
        level_format.setForeground(level_colors.get(level, QColor("#ffffff")))
        cursor.setCharFormat(level_format)
        cursor.insertText(f"{level}: ")
        
        # メッセージを追加
        message_format = QTextCharFormat()
        message_format.setForeground(QColor("#ffffff"))
        cursor.setCharFormat(message_format)
        cursor.insertText(f"{message}\n")
        
        # 自動スクロール
        if self.auto_scroll:
            self.log_display.setTextCursor(cursor)
            self.log_display.ensureCursorVisible()
    
    def clear_logs(self):
        """ログをクリア"""
        self.log_display.clear()
    
    def toggle_auto_scroll(self):
        """自動スクロールの切り替え"""
        self.auto_scroll = self.auto_scroll_button.isChecked()
        text = "自動スクロール: ON" if self.auto_scroll else "自動スクロール: OFF"
        self.auto_scroll_button.setText(text)
    
    def save_logs(self):
        """ログをファイルに保存"""
        from PyQt5.QtWidgets import QFileDialog
        
        # ファイル保存ダイアログ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"technical_fountain_log_{timestamp}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "ログファイルの保存",
            default_filename,
            "テキストファイル (*.txt);;すべてのファイル (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_display.toPlainText())
                self.append_log(f"ログを保存しました: {file_path}", "INFO")
            except Exception as e:
                self.append_log(f"ログの保存に失敗しました: {e}", "ERROR")