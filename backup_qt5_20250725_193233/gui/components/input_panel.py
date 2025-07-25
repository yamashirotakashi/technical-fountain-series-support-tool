"""入力パネルモジュール"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QGroupBox)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from utils.validators import Validators


class InputPanel(QWidget):
    """Nコード入力パネルウィジェット"""
    
    # カスタムシグナル
    process_requested = pyqtSignal(list)  # Nコードのリストを送信
    settings_requested = pyqtSignal()  # 設定ボタンクリック
    
    def __init__(self, parent=None):
        """
        InputPanelを初期化
        
        Args:
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UIを構築"""
        layout = QVBoxLayout(self)
        
        # グループボックス
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
        
        # 説明ラベル
        description_label = QLabel(
            "処理したいNコードを入力してください。\n"
            "複数のコードはカンマ（,）、タブ、スペース、または改行で区切ってください。\n"
            "例: N00001, N00002 または N00001[Tab]N00002 または各行に1つずつ"
        )
        description_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        
        # 入力エリア
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
        
        # ボタンレイアウト
        button_layout = QHBoxLayout()
        
        # 処理開始ボタン
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
        
        # クリアボタン
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
        
        # 設定ボタン
        self.settings_button = QPushButton("設定")
        self.settings_button.clicked.connect(self.on_settings_clicked)
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
        
        # ボタンを配置
        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addStretch()
        
        # グループレイアウトに追加
        group_layout.addWidget(description_label)
        group_layout.addWidget(self.n_code_input)
        group_layout.addLayout(button_layout)
        
        # メインレイアウトに追加
        layout.addWidget(group_box)
        layout.addStretch()
    
    def get_n_codes(self) -> list:
        """
        入力されたNコードのリストを取得
        
        Returns:
            有効なNコードのリスト
        """
        text = self.n_code_input.toPlainText()
        valid_codes, _ = Validators.validate_n_codes(text)
        return valid_codes
    
    def validate_input(self) -> bool:
        """
        入力を検証
        
        Returns:
            検証が成功した場合True
        """
        text = self.n_code_input.toPlainText()
        valid_codes, errors = Validators.validate_n_codes(text)
        
        if not text.strip():
            self.show_error("Nコードを入力してください。")
            return False
        
        if errors:
            error_message = "入力エラー:\n" + "\n".join(errors)
            self.show_error(error_message)
            return False
        
        if not valid_codes:
            self.show_error("有効なNコードが入力されていません。")
            return False
        
        return True
    
    def on_process_clicked(self):
        """処理開始ボタンがクリックされた時の処理"""
        if self.validate_input():
            n_codes = self.get_n_codes()
            self.process_requested.emit(n_codes)
    
    def clear_input(self):
        """入力をクリア"""
        self.n_code_input.clear()
    
    def on_settings_clicked(self):
        """設定ボタンがクリックされた時の処理"""
        self.settings_requested.emit()
    
    def show_error(self, message: str):
        """エラーメッセージを表示"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "入力エラー", message)
    
    def set_enabled(self, enabled: bool):
        """パネルの有効/無効を設定"""
        self.process_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)
        self.n_code_input.setEnabled(enabled)