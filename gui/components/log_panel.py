"""ログ表示パネルモジュール"""
from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat
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
                border: 1px solid #666;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:pressed {
                background-color: #333;
            }
        """)
        
        # エクスポートボタン
        self.export_button = QPushButton("ログ保存")
        self.export_button.clicked.connect(self.save_logs)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:pressed {
                background-color: #333;
            }
        """)
        
        # 自動スクロールチェックボックス
        from PyQt6.QtWidgets import QCheckBox
        self.auto_scroll_checkbox = QCheckBox("自動スクロール")
        self.auto_scroll_checkbox.setChecked(True)
        self.auto_scroll_checkbox.toggled.connect(self.toggle_auto_scroll)
        self.auto_scroll_checkbox.setStyleSheet("""
            QCheckBox {
                color: #333;
                font-size: 9pt;
            }
        """)
        
        # ボタンを配置
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.export_button)
        button_layout.addStretch()
        button_layout.addWidget(self.auto_scroll_checkbox)
        
        # メインレイアウトに追加
        layout.addWidget(self.log_display)
        layout.addLayout(button_layout)
    
    @pyqtSlot(str)
    def append_log(self, message: str):
        """
        ログメッセージを追加
        
        Args:
            message: ログメッセージ
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.log_display.append(formatted_message)
        
        if self.auto_scroll:
            # 最下部にスクロール
            scrollbar = self.log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    @pyqtSlot(str, str)
    def append_colored_log(self, message: str, level: str = "INFO"):
        """
        色付きログメッセージを追加
        
        Args:
            message: ログメッセージ
            level: ログレベル (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # カーソルを最後に移動
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # タイムスタンプを追加
        cursor.insertText(f"[{timestamp}] ")
        
        # レベルに応じて色を設定
        format = QTextCharFormat()
        if level == "ERROR":
            format.setForeground(QColor("#ff6b6b"))  # 赤
        elif level == "WARNING":
            format.setForeground(QColor("#ffd93d"))  # 黄
        elif level == "SUCCESS":
            format.setForeground(QColor("#6bcf7f"))  # 緑
        else:  # INFO
            format.setForeground(QColor("#ffffff"))  # 白
        
        # メッセージを挿入
        cursor.insertText(f"[{level}] {message}\n", format)
        
        if self.auto_scroll:
            # 最下部にスクロール
            scrollbar = self.log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    @pyqtSlot()
    def clear_logs(self):
        """ログをクリア"""
        self.log_display.clear()
        self.append_log("ログをクリアしました")
    
    @pyqtSlot()
    def save_logs(self):
        """ログをファイルに保存"""
        try:
            # ログディレクトリを作成
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            # ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = log_dir / f"techzip_log_{timestamp}.txt"
            
            # ログ内容を取得して保存
            log_content = self.log_display.toPlainText()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            self.append_colored_log(f"ログを保存しました: {filename}", "SUCCESS")
            
        except Exception as e:
            self.append_colored_log(f"ログ保存エラー: {str(e)}", "ERROR")
    
    @pyqtSlot(bool)
    def toggle_auto_scroll(self, enabled: bool):
        """
        自動スクロールを切り替え
        
        Args:
            enabled: 自動スクロールを有効にするかどうか
        """
        self.auto_scroll = enabled
        if enabled:
            self.append_log("自動スクロールを有効にしました")
        else:
            self.append_log("自動スクロールを無効にしました")
    
    def get_log_content(self) -> str:
        """
        現在のログ内容を取得
        
        Returns:
            ログの全内容
        """
        return self.log_display.toPlainText()